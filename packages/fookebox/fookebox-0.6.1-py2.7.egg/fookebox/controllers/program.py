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

import logging
import json

from datetime import time, datetime

from pylons import request, response, config, app_globals as g
from pylons.controllers.util import abort
from pylons.decorators import jsonify, rest

from fookebox.lib.base import BaseController, render
from fookebox.model import meta
from fookebox.model.jukebox import Jukebox
from fookebox.model.mpdconn import Track
from fookebox.model.schedule import Event, EVENT_TYPE_JUKEBOX

log = logging.getLogger(__name__)

class ProgramController(BaseController):

	@rest.restrict('GET')
	def index(self):
		jukebox = Jukebox()
		artists = jukebox.getArtists()
		genres = jukebox.getGenres()
		jukebox.close()

		return render('/program.tpl')

	@rest.restrict('GET')
	@jsonify
	def status(self):
		jukebox = Jukebox()
		event = jukebox.getCurrentEvent()
		next = jukebox.getNextEvent()

		now = datetime.now()
		if now.second % 2 > 0:
			format = "%H %M"
		else:
			format = "%H:%M"

		event = jukebox.getCurrentEvent()

		currentEvent = {
			'type': event.type,
			'title': event.name
		}

		if event.type == EVENT_TYPE_JUKEBOX:
			track = jukebox.getCurrentSong()

			if (track.artist == Track.NO_ARTIST and
						track.title == Track.NO_TITLE):
				track.artist = ''
				track.title = ''

			currentEvent['tracks'] = [{
				'artist': track.artist,
				'title': track.title,
			}]

			playlist = jukebox.getPlaylist()
			if len(playlist) > 1:
				track = Track()
				track.load(playlist[1])

				currentEvent['tracks'].append({
					'artist': track.artist,
					'title': track.title,
				})

		events = {'current': currentEvent}

		next = jukebox.getNextEvent()
		jukebox.close()

		if next:
			events['next'] = {
				'type': next.type,
				'title': next.name,
				'time': next.time.strftime("%H:%M")
			}

		return {
			'events': events,
			'time': now.strftime(format),
		}

	@rest.restrict('POST')
	def _edit_post(self):
		name = request.params['name']
		type = int(request.params['type'])
		hour = request.params['hour']
		minute = request.params['minute']
		dateTime = datetime.strptime("%s:%s" % (hour, minute),
				"%H:%M")
		if 'id' in request.params:
			id = request.params['id']
			Event.update(id, name, type, dateTime.time())
		else:
			Event.add(name, type, dateTime.time())

		return render('/program-edit.tpl',
		{
			'events': Event.all(),
			'current': Event.getCurrent()
		})


	@rest.dispatch_on(POST='_edit_post')
	@rest.restrict('GET')
	def edit(self):
		#if request.method == 'POST':
		#	pass

		event_q = meta.Session.query(Event)

		return render('/program-edit.tpl',
		{
			'events': Event.all(),
			'current': Event.getCurrent(),
			'edit': int(request.params.get('edit', 0))
		})

	@rest.restrict('POST')
	def current(self):
		try:
			post = json.load(request.environ['wsgi.input'])
		except ValueError:
			log.error("QUEUE: Could not parse JSON data")
			abort(400, 'Malformed JSON data')

		id = post.get('id')
		g.eventID = int(id)

		abort(204) # no content

	@rest.restrict('POST')
	def delete(self):
		try:
			post = json.load(request.environ['wsgi.input'])
		except ValueError:
			log.error("QUEUE: Could not parse JSON data")
			abort(400, 'Malformed JSON data')

		id = post.get('id')
		Event.delete(int(id))

		abort(204) # no content

	@rest.restrict('POST')
	def move(self):
		try:
			post = json.load(request.environ['wsgi.input'])
		except ValueError:
			log.error("QUEUE: Could not parse JSON data")
			abort(400, 'Malformed JSON data')

		id = post.get('id')
		direction = post.get('direction')

		if direction == 'up':
			Event.up(id)
		else:
			Event.down(id)

		abort(204) # no content
