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

import sys
import json
import base64
import socket
import logging

from pylons import config, cache, request, response
from pylons.decorators import jsonify, rest
from pylons.controllers.util import abort
from pylons.i18n.translation import _

from fookebox.lib.base import BaseController, render
from fookebox.model.jukebox import Jukebox, QueueFull
from fookebox.model.mpdconn import Album
from fookebox.model.albumart import AlbumArt

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)

class JukeboxController(BaseController):

	def __render(self, template, extra_vars):
		try:
			return render(template, extra_vars = extra_vars)
		except IOError:
			exctype, value = sys.exc_info()[:2]
			abort(500, value)

	def __search(self, where, what, forceSearch = False):
		log.debug("SEARCH: '%s' in '%s'" % (what, where))

		jukebox = Jukebox()
		tracks = jukebox.search(where, what, forceSearch)
		jukebox.close()

		log.debug("SEARCH: found %d track(s)" % len(tracks))
		return {'meta': {'what': what }, 'tracks': tracks}

	@rest.restrict('GET')
	def index(self):
		try:
			jukebox = Jukebox()
		except socket.error:
			log.error("Error on /index")
			return self.__render('/error.tpl', extra_vars={
				'error': 'Connection to MPD failed'})
		except:
			log.error("Error on /index")
			exctype, value = sys.exc_info()[:2]
			return self.__render('/error.tpl', extra_vars={
				'error': value})

		artists = jukebox.getArtists()
		genres = jukebox.getGenres()
		jukebox.close()

		user_agent = request.environ.get('HTTP_USER_AGENT')

		return self.__render('/client.tpl', extra_vars={
			'genres': genres,
			'artists': artists,
			'config': config,
			'mobile': 'mobile' in user_agent.lower(),
		})

	@rest.restrict('GET')
	@jsonify
	def status(self):
		jukebox = Jukebox()

		try:
			queueLength = jukebox.getQueueLength()
			enabled = jukebox.isEnabled()
			timeLeft = jukebox.timeLeft()
		except:
			log.error("Could not read status")
			jukebox.close()
			exctype, value = sys.exc_info()[:2]
			abort(500, value)

		if (config.get('auto_queue') and queueLength == 0 and enabled
			and timeLeft <= config.get('auto_queue_time_left')):
			try:
				jukebox.autoQueue()
			except:
				log.error("Auto-queue failed")
				jukebox.close()
				raise

		try:
			track = jukebox.getCurrentSong()
		except:
			log.error('Failed to get the current song')
			abort(500, _('Failed to get the current song'))
		finally:
			jukebox.close()

		data = {
			'queueLength': queueLength,
			'jukebox': enabled
		}

		if track:
			songPos = int(track.timePassed)
			songTime = track.time

			total = "%02d:%02d" % (songTime / 60, songTime % 60)
			position = "%02d:%02d" % (songPos / 60, songPos % 60)

			album = Album(track.artist, track.album)
			album.add(track)

			data['artist'] = track.artist
			data['track'] = track.title
			data['album'] = track.album
			data['has_cover'] = album.hasCover()
			data['cover_uri'] = album.getCoverURI()
			data['timePassed'] = position
			data['timeTotal'] = total
			data['playing'] = jukebox.isPlaying()

		return data

	@rest.restrict('POST')
	def enqueue(self):
		try:
			data = json.load(request.environ['wsgi.input'])
		except ValueError:
			log.error('ENQUEUE: Could not parse JSON data')
			abort(400, _('Malformed JSON data'))

		files = data.get('files')

		if not (files and len(files) > 0):
			log.error('ENQUEUE: No files specified')
			abort(400, _('No files specified'))

		jukebox = Jukebox()

		for file in files:
			if not file:
				log.error('ENQUEUE: Skipping empty file')
				abort(400, _('Missing file name'))

			try:
				jukebox.queue(file.encode('utf8'))
			except QueueFull:
				jukebox.close()
				log.error('ENQUEUE: Full, aborting')
				abort(409, _('The queue is full'))

		jukebox.close()

		abort(204) # no content

	@rest.dispatch_on(POST='enqueue')
	@rest.restrict('GET')
	@jsonify
	def queue(self):
		jukebox = Jukebox()
		items = jukebox.getPlaylist()
		jukebox.close()

		return {'queue': items[1:]}

	@rest.restrict('GET')
	@jsonify
	def genre(self, genreBase64=''):
		try:
			genre = genreBase64.decode('base64')
		except:
			log.error("GENRE: Failed to decode base64 data: %s" %
				genreBase64)
			abort(400, _('Malformed request'))

		return self.__search('genre', genre)

	@rest.restrict('GET')
	@jsonify
	def artist(self, artistBase64=''):
		try:
			artist = artistBase64.decode('base64')
		except:
			log.error("ARTIST: Failed to decode base64 data: %s" %
				artistBase64)
			abort(400, _('Malformed request'))

		return self.__search('artist', artist)

	@rest.restrict('POST')
	@jsonify
	def search(self):
		try:
			data = json.load(request.environ['wsgi.input'])
		except ValueError:
			log.error('SEARCH: Could not parse JSON data')
			abort(400, _('Malformed JSON data'))

		what = data.get('what')
		where = data.get('where')

		if not where:
			log.error("SEARCH: Incomplete JSON data")
			abort(400, _('Malformed request'))

		forceSearch = 'forceSearch' in data and data['forceSearch']

		return self.__search(where, what.encode('utf8'), forceSearch)

	@rest.restrict('POST')
	def remove(self):
		if not config.get('enable_song_removal'):
			log.error("REMOVE: Disabled")
			abort(403, _('Song removal disabled'))

		try:
			data = json.load(request.environ['wsgi.input'])
		except ValueError:
			log.error('REMOVE: Could not parse JSON data')
			abort(400, _('Malformed JSON data'))

		id = data.get('id')

		if not id:
			log.error('REMOVE: No id specified in JSON data')
			abort(400, _('Malformed request'))

		jukebox = Jukebox()
		jukebox.remove(id)
		jukebox.close()

		abort(204) # no content

	@rest.restrict('POST')
	def control(self):
		if not config.get('enable_controls'):
			log.error('CONTROL: Disabled')
			abort(403, _('Controls disabled'))

		try:
			data = json.load(request.environ['wsgi.input'])
		except ValueError:
			log.error('CONTROL: Could not parse JSON data')
			abort(400, _('Malformed JSON data'))

		action = data.get('action')

		if not action:
			log.error('CONTROL: No action specified in JSON data')
			abort(400, _('Malformed request'))

		log.debug('CONTROL: Action=%s' % action)

		jukebox = Jukebox()
		commands = {
			'play': jukebox.play,
			'pause': jukebox.pause,
			'prev': jukebox.previous,
			'next': jukebox.next,
			'voldown': jukebox.volumeDown,
			'volup': jukebox.volumeUp,
			'rebuild': jukebox.refreshDB,
		}

		if action not in commands:
			log.error('CONTROL: Invalid command')
			jukebox.close()
			abort(400, _('Invalid command'))

		try:
			commands[action]()
		except:
			log.error('Command %s failed' % action)
			abort(500, _('Command failed'))
		finally:
			jukebox.close()

		abort(204) # no content

	@rest.restrict('POST')
	@jsonify
	def findcover(self):
		try:
			data = json.load(request.environ['wsgi.input'])
		except ValueError:
			log.error('FINDCOVER: Could not parse JSON data')
			abort(400, _('Malformed JSON data'))

		artist = data.get('artist')
		album = data.get('album')

		album = Album(artist, album)

		if album.hasCover():
			return {'uri': album.getCoverURI()}

		abort(404, 'No cover')

	@rest.restrict('GET')
	def cover(self, artist, album):
		try:
			artist = base64.urlsafe_b64decode(artist.encode('utf8'))
			album = base64.urlsafe_b64decode(album.encode('utf8'))
		except:
			log.error("COVER: Failed to decode base64 data")
			abort(400, _('Malformed base64 encoding'))

		album = Album(artist.decode('utf8'), album.decode('utf8'))
		art = AlbumArt(album)
		path = art.get()

		if not path:
			log.error("COVER: missing for %s/%s" % (artist,
				album.name))
			abort(404, _('No cover found for this album'))

		file = open(path.encode('utf8'), 'r')
		data = file.read()
		file.close()

		response.headers['content-type'] = 'image/jpeg'
		return data

	@rest.restrict('GET')
	def disabled(self):
		return self.__render('/disabled.tpl', extra_vars={
			'config': config,
			'base_url': request.url.replace('disabled', ''),
		})
