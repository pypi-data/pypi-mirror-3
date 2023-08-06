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

// event types
var TYPE_JUKEBOX = 0;
var TYPE_BAND = 1;
var TYPE_DJ = 2;

var ProgramView = Class.create(AjaxView,
{
	sync: function()
	{
		setTimeout(this.sync.bind(this), 1000);
		this.get('program/status', this.applyStatus.bind(this));
	},
	applyStatus: function(transport)
	{
		var data = transport.responseJSON;

		$('clock').update(data.time);
		$('currentState').update(data.currentState);
		$('currentState').show();

		//var TYPE_JUKEBOX = 0;
		var events = data.events;
		var current = events.current;

		this.setCurrent(events.current);

		if (events.next) {
			this.setNext(events.next);
		} else {
			$('next').hide();
		}
	},
	setCurrent: function(event)
	{
		var name = event.title;

		switch (event.type)
		{
			case TYPE_JUKEBOX:
				var tracks = event.tracks;
				var artist = tracks[0].artist;
				var title = tracks[0].title;
				$('currentTitle').update(artist +" - "+ title);

				var box = $('currentState');
				if (tracks.length > 1) {
					var artist = tracks[1].artist;
					var track = tracks[1].title;

					box.update('next @ ' + name + ': ' +
						artist + ' - ' + track);
				} else {
					box.update(name);
				}
				break;
			case TYPE_BAND:
				$('currentTitle').update(name);
				$('currentState').update('live');
				break;
			case TYPE_DJ:
				$('currentTitle').update(name + ' [DJ]');
				$('currentState').update('live');
				break;
		}
	},
	setNext: function(event)
	{
		$('next').show();
		var title = event.title;

		switch (event.type)
		{
			case TYPE_JUKEBOX:
				$('nextTitle').update(title);
				break;
			case TYPE_BAND:
				$('nextTitle').update('LIVE BAND: ' + title);
				break;
			case TYPE_DJ:
				$('nextTitle').update(title + ' [DJ]');
				break;
		}
		$('nextTime').update(event.time);
	}
});

document.observe("dom:loaded", function()
{
	var prog = new ProgramView();
	prog.sync();
});
