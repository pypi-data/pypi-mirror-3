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
from mpd import MPDClient
from datetime import datetime
from threading import BoundedSemaphore
from pkg_resources import get_distribution, DistributionNotFound
from pylons.i18n.translation import _, ungettext

from pylons import config, app_globals as g
from fookebox.model.albumart import AlbumArt

log = logging.getLogger(__name__)

class Lock(object):

	class __impl:

		def __init__(self):
			self.semaphore = BoundedSemaphore(value=1)

		def acquire(self):
			return self.semaphore.acquire(False)

		def release(self):
			return self.semaphore.release()

	__instance = None

	def __init__(self):
		if Lock.__instance is None:
			Lock.__instance = Lock.__impl()

		self.__dict__['_Lock__instance'] = Lock.__instance

	def __getattr__(self, attr):
		return getattr(self.__instance, attr)

class Genre(object):

	def __init__(self, name):
		self.name = name
		self.base64 = base64.urlsafe_b64encode(name.encode('utf8'))

class Artist(object):

	def __init__(self, name):
		self.name = name
		self.base64 = base64.urlsafe_b64encode(name.encode('utf8'))

class Album(object):

	def __init__(self, artist, albumName, disc=None):
		self.isCompilation = False

		if albumName == None:
			self.name = ''
		else:
			self.name = albumName

		if artist == None:
			self.artist = ''
		else:
			self.artist = artist

		self.disc = disc
		self.tracks = []

	def add(self, track):
		if track.artist != self.artist and not (
			track.artist.startswith(self.artist) or
			self.artist.startswith(track.artist)):

			self.isCompilation = True
			self.artist = _('Various Artists').decode('utf8')

		self.tracks.append(track)

	def load(self):
		try:
			mpd = MPD.get()
			client = mpd.getWorker()

			data = client.find(
				'Artist', self.artist.encode('utf8'),
				'Album', self.name.encode('utf8'))
			client.release()
		except:
			client.release()
			raise

		for file in data:
			track = Track()
			track.load(file)
			self.add(track)

	def hasCover(self):
		art = AlbumArt(self)
		return art.get() != None

	def getCoverURI(self):
		artist = base64.urlsafe_b64encode(self.artist.encode('utf8'))
		name = base64.urlsafe_b64encode(self.name.encode('utf8'))
		return "%s/%s" % (artist, name)

	def getPath(self):
		basepath = config.get('music_base_path')

		if basepath == None:
			return None

		if len(self.tracks) > 0:
			track = self.tracks[0]
		else:
			self.load()
			if len(self.tracks) < 1:
				return None

			track = self.tracks[0]

		fullpath = os.path.join(basepath, track.file)
		return os.path.dirname(fullpath)

	def key(self):
		return "%s-%s" % (self.artist, self.name)

class Track(object):
	NO_ARTIST = 'Unknown artist'
	NO_TITLE = 'Unnamed track'

	track = 0

	def load(self, song):
		def __set(key, default):
			val = song.get(key, default)

			if val is None:
				return val

			if isinstance(val, list):
				val = val[0]

			if isinstance(val, int):
				return val
			else:
				return val.decode('utf8')

		self.artist = __set('artist', Track.NO_ARTIST)
		self.title = __set('title', Track.NO_TITLE)
		self.file = __set('file', '')
		self.disc = __set('disc', 0)
		self.album = __set('album', None)
		self.queuePosition = int(__set('pos', 0))
		self.time = int(__set('time', 0))

		if 'track' in song:
			# possible formats:
			#  - '12'
			#  - '12/21'
			#  - ['12', '21']
			t = song['track']
			if '/' in t:
				tnum = t.split('/')[0]
				self.track = int(tnum)
			elif isinstance(t, list):
				self.track = int(t[0])
			else:
				self.track = int(t)

	def __str__(self):
		return "%s - %s" % (self.artist, self.title)

class FookeboxMPDClient(MPDClient):

	def consume(self, do):
		self._docommand('consume', [do], self._getnone)

class MPDWorker(object):

	def __init__(self, num):
		self.num = num
		host = config.get('mpd_host')
		port = config.get('mpd_port')
		password = config.get('mpd_pass')

		try:
			pkg = get_distribution('python-mpd')
			if pkg.version < '0.3.0':
				self.mpd = FookeboxMPDClient()
			else:
				self.mpd = MPDClient()
		except DistributionNotFound:
			self.mpd = MPDClient()

		self.mpd.connect(host, port)

		if password:
			self.mpd.password(password)

		# enable consume on mpd in the first worker
		if num == 0:
			self.mpd.consume(1)

		self.atime = datetime.now()
		self.free = True

	def __del__(self):
		self.mpd.close()
		self.mpd.disconnect()

	def __str__(self):
		return "MPDWorker %d (last used: %s)" % (self.num, self.atime)

	def grab(self):
		self.free = False
		self.atime = datetime.now()

	def release(self):
		self.atime = datetime.now()
		self.free = True
		#log.debug("Worker %s released" % self)

	def __getattr__(self, attr):
		self.atime = datetime.now()
		return getattr(self.mpd, attr)

class MPDPool(object):

	lock = None

	def __init__(self):
		self.lock = BoundedSemaphore(value=1)
		self._workers = []

	def getWorker(self):
		self.lock.acquire()

		log.debug("Pool contains %d workers" % len(self._workers))

		for worker in self._workers:
			if worker.free:
				log.debug("Re-using worker %s" % worker)
				worker.grab()
				self._cleanup()
				self.lock.release()
				return worker
			else:
				log.debug("Worker %s is busy" % worker)
				now = datetime.now()
				diff = (now - worker.atime).seconds

				# TODO: here we manipulate the collection that
				# we are iterating over - probably a bad idea
				if diff > 30:
					log.warn("Terminating stale worker")
					worker.release()
					self._workers.remove(worker)

		try:
			worker = MPDWorker(len(self._workers))
			log.debug("Created new worker %s" % worker)
			worker.grab()
			self._workers.append(worker)
			self.lock.release()
			return worker

		except Exception:
			log.fatal('Could not connect to MPD')
			self.lock.release()
			raise

	def _cleanup(self):
		now = datetime.now()

		for worker in self._workers:
			if worker.free:
				if (now - worker.atime).seconds > 10:
					log.debug("Removing idle worker %s" %
							worker)
					self._workers.remove(worker)

class MPD(object):
	@staticmethod
	def get():
		if g.mpd == None:
			g.mpd = MPDPool()

		return g.mpd
