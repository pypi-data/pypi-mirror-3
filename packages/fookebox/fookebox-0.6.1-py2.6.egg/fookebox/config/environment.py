"""Pylons environment configuration"""
import os

from mako.lookup import TemplateLookup
from pylons.configuration import PylonsConfig
from pylons.error import handle_mako_error
from paste.deploy.converters import asbool

from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool

from fookebox.model import init_model

import fookebox.lib.app_globals as app_globals
import fookebox.lib.helpers
from fookebox.config.routing import make_map

def load_environment(global_conf, app_conf):
	"""Configure the Pylons environment via the ``pylons.config``
	object
	"""
	config = PylonsConfig()

	# Pylons paths
	root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	paths = dict(root=root,
			controllers=os.path.join(root, 'controllers'),
			static_files=os.path.join(root, 'public'),
			templates=[os.path.join(root, 'templates')])

	# Initialize config with the basic options
	config.init_app(global_conf, app_conf, package='fookebox', paths=paths)

	config['routes.map'] = make_map(config)
	config['pylons.app_globals'] = app_globals.Globals(config)
	config['pylons.h'] = fookebox.lib.helpers

	# Setup cache object as early as possible
	import pylons
	pylons.cache._push_object(config['pylons.app_globals'].cache)

	# Create the database engine
	engine = engine_from_config(config, 'sqlalchemy.', poolclass=NullPool)
	init_model(engine)

	# Create the Mako TemplateLookup, with the default auto-escaping
	config['pylons.app_globals'].mako_lookup = TemplateLookup(
		directories=paths['templates'],
		error_handler=handle_mako_error,
		module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
		input_encoding='utf-8', default_filters=['escape'],
		imports=['from webhelpers.html import escape'])

	import pkg_resources
	config['version'] = pkg_resources.get_distribution("fookebox").version

	# CONFIGURATION OPTIONS HERE (note: all config options will override
	# any Pylons config options)

	default_strings = {
		'site_name': 'fookebox',
		'mpd_host': 'localhost',
		'compliations_name': 'Various Artists',
	}
	default_ints = {
		'mpd_port': 6600,
		'max_queue_length': 4,
		'auto_queue_time_left': 1,
	}
	default_bools = {
		'auto_queue': True,
		'auto_queue_random': False,
		'show_search_tab': True,
		'enable_controls': True,
		'enable_song_removal': True,
		'enable_queue_album': True,
		'find_over_search': False,
		'cache_cover_art': False,
		'hide_credits': False,
		'show_cover_art': True,
	}

	for key in default_strings:
		if key not in config:
			config[key] = default_strings[key]

	for key in default_ints:
		if key in config and config[key].isdigit():
			config[key] = int(config[key])
		else:
			config[key] = default_ints[key]

	for key in default_bools:
		if key in config:
			try:
				config[key] = asbool(config[key])
			except:
				config[key] = default_bools[key]
		else:
			config[key] = default_bools[key]

	return config
