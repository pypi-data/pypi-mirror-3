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

/* the base class for all our views */

var AjaxView = Class.create(
{
	get: function(url, onsuccess)
	{
		var time = new Date().getTime();

		new Ajax.Request(url + '?ms=' + time,
		{
			method: 'get',
			requestHeaders: { 'Accept': 'application/json' },
			onSuccess: onsuccess,
			onFailure: this.transportError.bind(this),
		});
	},
	post: function(url, data, onsuccess, onfailure)
	{
		if (!onfailure)
			onfailure = this.transportError.bind(this);

		var time = new Date().getTime();

		new Ajax.Request(url + '?ms=' + time,
		{
			method: 'post',
			requestHeaders: { 'Accept': 'application/json' },
			postBody: Object.toJSON(data),
			contentType: 'application/json',
			onSuccess: onsuccess,
			onFailure: onfailure,
		});
	},
	transportError: function(transport)
	{
		var response = transport.responseText;

		if (!response)
			response = 'Something bad happened';

		new Message(response).show();
		this.hideProgressbar();
	},
	showProgressbar: function()
	{
		$('progress').show();
	},
	hideProgressbar: function()
	{
		if ($('progress'))
			$('progress').hide();
	},
});

/* message class */

var Message = Class.create(
{
	initialize: function(text)
	{
		this.text = text;
	},
	show: function()
	{
		if ($('messageText').timeout)
		{
			clearTimeout($('messageText').timeout);
		}

		$('messageText').update(this.text);
		$('messageText').timeout = setTimeout(this.hide, 3000);
		Effect.Appear('message', { 'duration' : '0.1' });
	},
	hide: function()
	{
		Effect.Fade('message', { 'duration' : '0.4' });
	},
});
