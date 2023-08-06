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

var DisabledJukebox = Class.create(AjaxView,
{
	reload: function(transport)
	{
		window.location.reload();
	},
	parseStatus: function(transport)
	{
		var data = transport.responseJSON;
		var jukebox = data.jukebox;

		if (jukebox)
		{
			var url = window.location.href;
			var base = url.substring(0, url.length - 8);
			window.location = base;
		}
	},
	sync: function(transport)
	{
		setTimeout(this.sync.bind(this), 1000);
		this.get('status', this.parseStatus.bind(this));
	}
});

document.observe("dom:loaded", function()
{
	jukebox = new DisabledJukebox();
	jukebox.sync();
});
