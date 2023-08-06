/*
 * fookebox, http://fookebox.googlecode.com/
 *
 * Copyright (C) 2007-2011 Stefan Ott. All rights reserved.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

var ScheduleView = Class.create(AjaxView,
{
	reload: function(transport)
	{
		window.location.reload();
	},
	setCurrent: function(eventId)
	{
		var data = $H({'id': eventId});
		this.post('schedule/current', data, this.reload);
	},
	remove: function(eventId)
	{
		if (!confirm('Delete this event?')) {
			return
		}

		var data = $H({'id': eventId});
		this.post('schedule/delete', data, this.reload);
	},
	moveUp: function(eventId)
	{
		var data = $H({
			'id': eventId,
			'direction': 'up'
		});
		this.post('schedule/move', data, this.reload);
	},
	moveDown: function(eventId)
	{
		var data = $H({
			'id': eventId,
			'direction': 'down'
		});
		this.post('schedule/move', data, this.reload);
	},
});

document.observe("dom:loaded", function()
{
	prog = new ScheduleView();
});
