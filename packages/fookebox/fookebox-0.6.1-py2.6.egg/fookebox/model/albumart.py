# fookebox, http://fookebox.googlecode.com/
#
# Copyright (C) 2007-2011 Stefan Ott. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import os
import base64
import logging
from datetime import datetime
from threading import BoundedSemaphore

from pylons import config, cache

from fookebox.lib.util import FileSystem as fs

log = logging.getLogger(__name__)

class AlbumArt(object):
	def __init__(self, album):
		self.album = album

	def _getRockboxPath(self, compilation=False):
		pattern = re.compile('[\/:<>\?*|]')
		album = pattern.sub('_', self.album.name)

		if compilation:
			artist = pattern.sub('_', config.get(
				'compliations_name'))
		else:
			artist = pattern.sub('_', self.album.artist)

		return "%s/%s-%s.jpg" % (config.get('album_cover_path'),
				artist, album)

	def _getRhythmboxPath(self, compilation=False):
		album = self.album.name.replace('/', '-')

		if compilation:
			artist = config.get('compliations_name').replace(
					'/', '-')
		else:
			artist = self.album.artist.replace('/', '-')

		return "%s/%s - %s.jpg" % (config.get('album_cover_path'),
				artist, album)

	def _getInDirCover(self):
		path_cache = cache.get_cache('album_path', type='memory')
		key = self.album.key()

		dirname = path_cache.get_value(key=key,
			createfunc=self.album.getPath, expiretime=60)

		if dirname == None:
			return None

		def best_image(x, y):
			pattern = '(cover|album|front)'

			if re.match(pattern, x, re.I):
				return x
			else:
				return y

		if not (fs.exists(dirname) and fs.isdir(dirname)):
			return None

		dir = fs.listdir(dirname)
		dir = filter(lambda x: x.endswith(
			('jpg', 'JPG', 'jpeg', 'JPEG')), dir)

		if len(dir) < 1:
			return None

		bestmatch = reduce(best_image, dir)
		return os.path.join(dirname, bestmatch)

	def get(self):
		if config.get('cache_cover_art'):
			cover_path_cache = cache.get_cache('cover_path')
			song = "%s - %s" % (str(self.album.artist),
					str(self.album.name))
			path = cover_path_cache.get_value(key=song,
				createfunc=self._getCover, expiretime=300)

			if path == None:
				cover_path_cache.remove_value(song)
		else:
			path = self._getCover()

		return path

	def _getCover(self):
		if not config.get('show_cover_art'):
			return None

		if config.get('album_cover_path'):
			path = self._getRockboxPath()
			if fs.exists(path):
				return path

			path = self._getRockboxPath(True)
			if fs.exists(path):
				return path

			path = self._getRhythmboxPath()
			if fs.exists(path):
				return path

			path = self._getRhythmboxPath(True)
			if fs.exists(path):
				return path

		if config.get('music_base_path'):
			return self._getInDirCover()

		return None
