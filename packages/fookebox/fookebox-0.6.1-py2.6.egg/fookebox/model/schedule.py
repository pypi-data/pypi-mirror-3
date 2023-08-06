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

import logging
import sqlalchemy as sa
from sqlalchemy import orm

from fookebox.model import meta
from pylons import app_globals as g

log = logging.getLogger(__name__)

t_event = sa.Table("Events", meta.metadata,
	sa.Column("id", sa.types.Integer, primary_key=True),
	sa.Column("index", sa.types.Integer, primary_key=False),
	sa.Column("type", sa.types.Integer, nullable=False),
	sa.Column("name", sa.types.String(100), nullable=False),
	sa.Column("time", sa.types.Time, nullable=False),
)

EVENT_TYPE_JUKEBOX = 0
EVENT_TYPE_BAND = 1
EVENT_TYPE_DJ = 2

class Event(object):
	def __str__(self):
		return "[type %s] %s @ %s (index=%d)" % (
				self.type, self.name, self.time, self.index)

	@staticmethod
	def currentID():
		id = g.eventID;
		if id == None:
			events = Event.all()
			if len(events) > 0:
				g.eventID = events[0].id
			else:
				return -1

		return g.eventID

	@staticmethod
	def all():
		event_q = meta.Session.query(Event)
		return event_q.order_by(Event.index.asc()).all()

	@staticmethod
	def get(id):
		event_q = meta.Session.query(Event)
		return event_q.get(id)

	@staticmethod
	def getCurrent():
		event_q = meta.Session.query(Event)
		event = event_q.get(Event.currentID())

		if event == None:
			event = Event()
			event.name = 'fookebox jukebox'
			event.type = EVENT_TYPE_JUKEBOX
			event.index = 0

		return event

	@staticmethod
	def getNext():
		event_q = meta.Session.query(Event)
		current = Event.getCurrent()
		events = event_q.filter(Event.index > current.index)
		return events.order_by(Event.index.asc()).first()

	@staticmethod
	def delete(id):
		event_q = meta.Session.query(Event)
		event = event_q.get(id)

		log.info("Deleting event %s" % event)

		meta.Session.delete(event)
		meta.Session.commit()

	@staticmethod
	def add(name, type, time):
		event = Event()
		event.name = name
		event.type = type
		event.time = time
		meta.Session.add(event)
		meta.Session.commit()

		event.index = event.id
		meta.Session.commit()

		log.info("Created event %s" % event)

	@staticmethod
	def update(id, name, type, time):
		event_q = meta.Session.query(Event)
		event = event_q.get(id)
		event.name = name
		event.type = type
		event.time = time
		meta.Session.commit()

	@staticmethod
	def up(id):
		event_q = meta.Session.query(Event)
		event = event_q.get(id)

		prev = event_q.filter(Event.index < event.index).order_by(
			Event.index.desc()).first()

		if prev != None:
			tmp = prev.index
			prev.index = event.index
			event.index = tmp
			meta.Session.commit()

	@staticmethod
	def down(id):
		event_q = meta.Session.query(Event)
		event = event_q.get(id)

		next = event_q.filter(Event.index > event.index).order_by(
			Event.index.asc()).first()

		if next != None:
			tmp = next.index
			next.index = event.index
			event.index = tmp
			meta.Session.commit()

orm.mapper(Event, t_event)

