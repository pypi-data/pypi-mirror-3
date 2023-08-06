"""Setup the fookebox application"""
import logging

import pylons.test

from fookebox.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
	"""Place any commands to setup fookebox here"""
	# Don't reload the app if it was loaded under the testing environment
	if not pylons.test.pylonsapp:
		load_environment(conf.global_conf, conf.local_conf)

	from fookebox.model import meta
	log.info("Creating tables")
	meta.metadata.create_all(bind=meta.engine)
	log.info("Successfully setup")
