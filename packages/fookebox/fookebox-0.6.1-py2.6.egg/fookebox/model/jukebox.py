# fookebox, http://fookebox.googlecode.com/
#
# Copyright (C) 2007-2012 Stefan Ott. All rights reserved.
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
import sys
import random
import logging

from pylons import config, app_globals as g

from mpdconn import *
from schedule import Event, EVENT_TYPE_JUKEBOX

log = logging.getLogger(__name__)

class QueueFull(Exception):
	pass

class Jukebox(object):
	client = None
	lastAutoQueued = -1

	def __init__(self, mpd=None):
		self._connect(mpd)

	def _connect(self, to=None):
		if not to == None:
			self.client = to
			return

		mpd = MPD.get()
		self.client = mpd.getWorker()

	def close(self):
		self.client.release()

	def timeLeft(self):
		status = self.client.status()

		if 'time' not in status:
			return 0

		(timePlayed, timeTotal) = status['time'].split(':')
		timeLeft = int(timeTotal) - int(timePlayed)
		return timeLeft

	def queue(self, file):
		log.info("Queued %s" % file)

		if self.getQueueLength() >= config.get('max_queue_length'):
			raise QueueFull()

		self.client.add(file)

		# Prevent (or reduce the probability of) a race-condition where
		# the auto-queue functionality adds a new song *after* the last
		# one stopped playing (which would re-play the previous song)
		if not self.isPlaying() and len(self.getPlaylist()) > 1:
			self.client.delete(0)

		self.client.play()

	def _autoQueueRandom(self):
		genre = config.get('auto_queue_genre')

		if genre:
			songs = self.client.search('Genre', str(genre))
		else:
			songs = self.client.listall()

		if len(songs) < 1:
			return

		file = []

		while 'file' not in file:
			# we might have to try several times in case we get
			# a directory instead of a file
			index = random.randrange(len(songs))
			file = songs[index]

		self.queue(file['file'])

	def _autoQueuePlaylist(self, playlist):
		self.client.load(playlist)

		if len(playlist) < 1:
			return

		if config.get('auto_queue_random'):
			self.client.shuffle()
			playlist = self.client.playlist()
			song = playlist[0]
		else:
			playlist = self.client.playlist()
			index = (Jukebox.lastAutoQueued + 1) % len(playlist)
			song = playlist[index]
			Jukebox.lastAutoQueued += 1

		self.client.clear()
		self.queue(song)
		log.debug(Jukebox.lastAutoQueued)

	def autoQueue(self):
		log.info("Auto-queuing")
		lock = Lock()
		if not lock.acquire():
			return

		playlist = config.get('auto_queue_playlist')
		if playlist == None:
			self._autoQueueRandom()
		else:
			self._autoQueuePlaylist(playlist)

		lock.release()

	def search(self, where, what, forceSearch = False):
		if config.get('find_over_search') and not forceSearch:
			return self.client.find(where, what)

		return self.client.search(where, what)

	def getPlaylist(self):
		playlist = self.client.playlistinfo()
		return playlist

	def getGenres(self):
		genres = sorted(self.client.list('genre'))
		return [Genre(genre.decode('utf8')) for genre in genres]

	def getArtists(self):
		artists = sorted(self.client.list('artist'))
		return [Artist(artist.decode('utf8')) for artist in artists]

	def isPlaying(self):
		status = self.client.status()
		return status['state'] == 'play'

	def getCurrentSong(self):
		current = self.client.currentsong()

		if current == None:
			return None

		status = self.client.status()
		if 'time' in status:
			time = status['time'].split(':')[0]
		else:
			time = 0

		track = Track()
		track.load(current)
		track.timePassed = time

		return track

	def getQueueLength(self):
		playlist = self.client.playlist()
		return max(len(playlist) - 1, 0)

	def getCurrentEvent(self):
		event = Event.getCurrent()
		event.jukebox = self
		return event

	def getNextEvent(self):
		event = Event.getNext()
		return event

	def isEnabled(self):
		event = self.getCurrentEvent()
		return event.type == EVENT_TYPE_JUKEBOX

	def remove(self, id):
		log.info("Removing playlist item #%d" % id)
		self.client.delete(id)

	def play(self):
		self.client.play()

	def pause(self):
		self.client.pause()

	def previous(self):
		self.client.previous()

	def next(self):
		# This is to prevent interruptions in the audio stream
		# See http://code.google.com/p/fookebox/issues/detail?id=6
		if self.getQueueLength() < 1 and config.get('auto_queue'):
			self.autoQueue()

		self.client.next()

	def volumeDown(self):
		status = self.client.status()
		volume = int(status.get('volume', 0))
		self.client.setvol(max(volume - 5, 0))

	def volumeUp(self):
		status = self.client.status()
		volume = int(status.get('volume', 0))
		self.client.setvol(min(volume + 5, 100))

	def refreshDB(self):
		self.client.update()
