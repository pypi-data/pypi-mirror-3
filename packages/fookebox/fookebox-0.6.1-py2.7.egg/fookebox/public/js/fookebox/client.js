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

var QueueView = Class.create(AjaxView,
{
	initialize: function(songRemoval)
	{
		this.songRemoval = songRemoval;
		this.queueLength = -1;
		this.queueView = $('playlist');
		this.template = new Template('#{artist} - #{title} ');
	},
	sync: function()
	{
		this.get('queue', this.update.bind(this));
	},
	update: function(transport)
	{
		var data = transport.responseJSON;
		var queue = data.queue;
		this.queueLength = queue.length;

		var playlist = this.queueView.select('li');

		playlist.each(function(li, index)
		{
			var item = queue[index];

			if (item) {
				this.updateSlot(li, index, item);
			} else {
				li.update('<span class="freeSlot">-- ' +
						_('empty') + ' --</span>');
			}
		}.bind(this));
	},
	updateSlot: function(element, position, track)
	{
		if (!track.artist || track.artist.blank())
			track.artist = _('Unknown artist');
		if (!track.title || track.title.blank())
			track.title = _('Unnamed track');

		element.update(this.template.evaluate(track));

		if (this.songRemoval)
		{
			var link = new Element('a', {'href': '#'});
			link.onclick = function()
			{
				this.unqueue(position + 1);
				return false;
			}.bind(this);

			var img = new Element('img', {
				'alt': 'x',
				'src': 'img/delete.png',
				'title': _('Remove from the queue'),
			});
			link.appendChild(img);
			element.appendChild(link);
		}
	},
	setLength: function(length)
	{
		if (length != this.queueLength)
			this.sync();
	},
	unqueue: function(id)
	{
		var data = $H({'id': id});
		this.post('remove', data, this.sync.bind(this));
	},
});

var TrackView = Class.create(AjaxView,
{
	initialize: function()
	{
		this.artist = "";
		this.track = "";
		this.timeTotal = "00:00";
		this.playing = false;

		this.time = new Date(0, 0, 0);
	},
	attach: function(jukebox)
	{
		this.artistView = $('artist');
		this.trackView = $('track');
		this.timeView = $('timeTotal');
		this.timePassedView = $('timePassed');

		function addControl(key) {
			$('control-' + key).onclick = function() {
				jukebox.control(key); return false
			};
		}

		if ($('control')) {
			addControl('prev');
			addControl('pause');
			addControl('play');
			addControl('next');
			addControl('voldown');
			addControl('volup');
			addControl('rebuild');
		}
	},
	updateTime: function()
	{
		var seconds = this.time.getSeconds();
		var minutes = this.time.getMinutes();

		if (seconds < 10)
			seconds = "0" + seconds;
		if (minutes < 10)
			minutes = "0" + minutes;

		this.timePassedView.update(minutes + ":" + seconds);
	},
	tick: function()
	{
		if (this.playing)
			this.time.setSeconds(this.time.getSeconds() + 1);
		this.updateTime();
	},
	adjustTime: function(time)
	{
		// sync our client-side track time with the one from the
		// server. update the seconds only if we differ by more than
		// one second (force-update the display in that case).
		//
		// this should fix the 'jumpy' track time display
		var parts = time.split(':');
		if (parts.length == 2)
		{
			var minutes = parts[0];
			var seconds = parts[1];

			var diff = seconds - this.time.getSeconds();

			this.time.setMinutes(minutes);

			if (diff > 1 || diff < -1)
			{
				this.time.setSeconds(seconds);
				this.updateTime();
			}
		}

	},
	update: function(artist, track, timeTotal, playing)
	{
		this.artist = artist;
		this.track = track;
		this.timeTotal = timeTotal;
		this.playing = playing;

		if (!this.playing)
		{
			Effect.Pulsate('timePassed', {pulses: 1, duration: 1});
		}

		if (this.artist != this.artistView.innerHTML)
			this.artistView.update(this.artist);
		if (this.track != this.trackView.innerHTML)
			this.trackView.update(this.track);
		if (this.timeTotal != this.timeView.innerHTML)
			this.timeView.update(this.timeTotal);
	},
});

var CoverView = Class.create(AjaxView,
{
	setCover: function(hasCover, coverURI)
	{
		var img = $('nowPlayingCover');
		if (hasCover) {
			img.src = 'cover/' + coverURI;
			img.show();
		} else {
			img.hide();
		}
	}
});

var MusicView = Class.create(AjaxView,
{
	initialize: function(jukebox)
	{
		this.jukebox = jukebox;
	},
	attach: function()
	{
		$$('.artistLink').each(function(link) {
			link.onclick = function() {
				var target = event.target;
				var artist = target.id.substring(7, target.id.length);
				this.showArtist(artist);
				return false;
			}.bind(this);
		}.bind(this));

		$$('.genreLink').each(function(link) {
			link.onclick = function() {
				var target = event.target;
				var genre = target.id.substring(6, target.id.length);
				this.showGenre(genre);
				return false;
			}.bind(this);
		}.bind(this));

		$('searchForm').onsubmit = function(event) {
			var form = event.target;
			this.search(form);
			return false;
		}.bind(this);
	},
	showArtist: function(artist)
	{
		this.showProgressbar();

		// TODO: the page control should actually do this
		window.location = "#artist=" + artist;
		this.jukebox.page.url = window.location.href;

		this.get('artist/' + artist, this.showSearchResult.bind(this));
	},
	showGenre: function(genre)
	{
		this.showProgressbar();

		// TODO: the page control should actually do this
		window.location = "#genre=" + genre;
		this.jukebox.page.url = window.location.href;

		this.get('genre/' + genre, this.showSearchResult.bind(this));
	},
	search: function(form)
	{
		this.showProgressbar();

		var type = $F(form.searchType);
		var term = $F(form.searchTerm);

		var data = $H({
			'where': type,
			'what':  term,
			'forceSearch': true
		});

		this.post('search', data, this.showSearchResult.bind(this));
	},
	showSearchResult: function(transport)
	{
		var result = new SearchResult(this.jukebox, transport);
		result.show();
		this.hideProgressbar();
	}
});

var AlbumCover = Class.create(AjaxView,
{
	initialize: function(album, target)
	{
		this.album = album;
		this.target = target;
	},
	load: function()
	{
		var data = $H({
			'artist': this.album.artist,
			'album': this.album.name
		});

		this.post('findcover', data, this.loaded.bind(this),
							this.hide.bind(this));
	},
	loaded: function(transport)
	{
		var response = transport.responseJSON;
		this.target.src = 'cover/' + response.uri;
	},
	hide: function(transport)
	{
		this.target.style.display = 'None';
	}
});

var SearchResult = Class.create(
{
	initialize: function(jukebox, transport)
	{
		this.jukebox = jukebox;

		this.tracks = transport.responseJSON.tracks;
		this.what = transport.responseJSON.meta.what;

		if (!this.what || this.what.blank())
			this.what = _('(none)');

		this.albums = new Hash();

		this.trackTemplate = new Template
					('#{track} - #{artist} - #{title}');
		this.albumTemplate = new Template
					('#{artist} - #{name}');
		this.albumDiscTemplate = new Template
					('#{artist} - #{name} (Disc #{disc})');

		this.parseAlbums();
	},
	parseAlbums: function()
	{
		this.tracks.each(function(track)
		{
			// Yes, this sucks: python-mpd enjoys returning arrays
			// when multiple tags are present. We need to unpack
			// them here.

			if (Object.isArray(track.album))
				track.album = track.album[0];
			if (Object.isArray(track.artist))
				track.artist = track.artist[0];
			if (Object.isArray(track.title))
				track.title = track.title[0];
			if (Object.isArray(track.track))
				track.track = track.track[0];

			var key = track.album + "-" + track.disc;
			var album = this.albums.get(key);

			if (album == null)
			{
				album = new Album(track.artist, track.album,
					track.disc);
				this.albums.set(key, album);
			}

			album.add(track);
		}, this);
	},
	showTrack: function(track)
	{
		var node = new Element('li', {'class': 'track'});
		var link = new Element('a', {'href': '#'});

		link.update(this.trackTemplate.evaluate(track));
		link.onclick = function(event)
		{
			this.jukebox.queue(track);
			return false;
		}.bind(this);

		node.appendChild(link);
		return node;
	},
	showAlbum: function(album)
	{
		var node = new Element('li', {'class': 'searchResultItem'});
		var header = new Element('h3', {'class': 'album'});
		var tracks = new Element('ul', {'class': 'trackList'});
		var coverArt = new Element('img', {'class': 'coverArt',
			'width': 200});

		if (this.jukebox.config.get('enable_queue_album'))
		{
			var link = new Element('a', {'href': '#'});

			link.onclick = function(event)
			{
				this.jukebox.queueAlbum(album);
				return false;
			}.bind(this);

			var template = album.disc ? this.albumDiscTemplate :
							this.albumTemplate;

			link.update(template.evaluate(album));
			header.appendChild(link);
		}
		else
		{
			header.update(this.albumTemplate.evaluate(album));
		}

		album.getTracks().each(function(track)
		{
			tracks.appendChild(this.showTrack(track));
		}, this);

		if (this.jukebox.config.get('show_cover_art'))
			new AlbumCover(album, coverArt).load();

		node.appendChild(coverArt);
		node.appendChild(header);
		node.appendChild(tracks);
		return node;
	},
	show: function(transport)
	{
		// TODO: this, right
		$('searchResult').update('');

		var header = new Element('h2').update(this.what);
		var ul = new Element('ul', {'id': 'searchResultList'});

		var sorted = this.albums.values().sortBy(function(s)
		{
			return s.artist + ' - ' + s.name;
		});

		sorted.each(function(album)
		{
			ul.appendChild(this.showAlbum(album));
		}, this);

		$('searchResult').appendChild(header);
		$('searchResult').appendChild(ul);
	},
});

var Album = Class.create(
{
	initialize: function(artist, name, disc)
	{
		this.artist = artist;
		this.name = name;
		this.disc = disc;
		this.tracks = new Hash();

		if (!this.artist || this.artist.blank())
			this.artist = _('Unknown artist');
		if (!this.name || this.name.blank())
			this.name = _('Unnamed album');
	},
	add: function(track)
	{
		if (!track.track)
			track.track = '00';
		if (track.track.include('/'))
			track.track = track.track.sub(/\/.*/, '');
		if (track.track < 10 && track.track.length == 1)
			track.track = '0' + track.track;

		if (!track.artist || track.artist.blank())
			track.artist = _('Unknown artist');
		if (!track.title || track.title.blank())
			track.title = _('Unnamed track');

		if ((track.artist != this.artist) &&
					!track.artist.startsWith(this.artist))
		{
			if (this.artist.startsWith(track.artist))
				this.artist = track.artist;
			else
				this.artist = _('Various artists');
		}

		this.tracks.set(track.file, track);
	},
	getTracks: function()
	{
		return this.tracks.values().sortBy(function(s)
		{
			return s.track;
		});

	}
});

var JukeboxView = Class.create(AjaxView,
{
	initialize: function(config)
	{
		this.config = new Hash();
		this.loadconfig();

		this.queueView = new QueueView(
				this.config.get('enable_song_removal'));
		this.trackView = new TrackView();
		this.coverView = new CoverView();
		this.musicView = new MusicView(this);
		this.page = new PageControl(this);
		this.page.watch();
	},
	loadconfig: function()
	{
		setbool = function(key, value)
		{
			if (Object.isUndefined(value))
				this.config.set(key, false);
			else
				this.config.set(key, $F(value) == 'True');
		}.bind(this);

		var form = $('config');
		setbool('enable_queue_album', form.enable_queue_album);
		setbool('show_cover_art', form.show_cover_art);
		setbool('enable_song_removal', form.enable_song_removal);
	},
	attach: function()
	{
		this.trackView.attach(this);
		this.musicView.attach();
	},
	disable: function()
	{
		window.location = 'disabled';
	},
	readStatus: function(transport)
	{
		var data = transport.responseJSON;
		var enabled = data.jukebox;

		if (!enabled)
		{
			this.disable();
			return
		}

		this.trackView.update(data.artist, data.track, data.timeTotal,
								data.playing);
		this.trackView.adjustTime(data.timePassed);
		this.coverView.setCover(data.has_cover, data.cover_uri);
		this.queueView.setLength(data.queueLength);
	},
	sync: function()
	{
		window.setTimeout(this.sync.bind(this), 1000);

		// update time
		this.trackView.tick();

		this.get('status', this.readStatus.bind(this));
	},
	control: function(action)
	{
		var data = $H({'action': action});
		this.post('control', data, function(transport) {});
	},
	queue: function(track)
	{
		this.queueAll($A([track.file]));
	},
	queueAlbum: function(album)
	{
		this.queueAll(album.getTracks().pluck('file'));
	},
	queueAll: function(tracks)
	{
		var data = $H({'files': tracks});
		this.post('queue', data,
			this.queueView.sync.bind(this.queueView));
	},
	showArtist: function(artist)
	{
		// TODO: remove this
		this.musicView.showArtist(artist);
	},
	showGenre: function(genre)
	{
		// TODO: remove this
		this.musicView.showGenre(genre);
	},
});

var PageControl = Class.create(
{
	initialize: function(jukebox)
	{
		this.tab = 'artist';
		this.url = '';
		this.jukebox = jukebox;
	},
	watch: function()
	{
		this.url = window.location.href;
		this.apply();
		this.update();

		this.attachToTab('artist');
		this.attachToTab('genre');
		this.attachToTab('search');
	},
	attachToTab: function(tab)
	{
		var li = $(tab + 'Tab');

		if (!li)
			return;

		var a = li.select('a');

		if (a.length > 0) {
			a[0].onclick = function() {
				this.setTab(tab);
				return false;
			}.bind(this);
		}
	},
	update: function()
	{
		setTimeout(this.update.bind(this), 400);

		var url = window.location.href;

		if (url != this.url)
		{
			this.url = url;
			this.apply();
		}
	},
	apply: function()
	{
		url = unescape(this.url);

		if (url.indexOf("#") > -1)
		{
			var parts = url.split('#');
			var params = parts[1].split('=');
			var key = params[0];
			var value = parts[1].substring(key.length + 1);

			if (key == 'artist') {
				this.setTab(key);
				this.jukebox.showArtist(value);
			} else if (key == 'genre') {
				this.setTab(key);
				this.jukebox.showGenre(value);
			} else if (key == 'tab') {
				this.setTab(value);
			}
		}
	},
	setTab: function(name)
	{
		if (name == this.tab) return;

		$(name + 'List').show();
		$(this.tab + 'List').hide();

		$(name + 'Tab').className = 'active';
		$(this.tab + 'Tab').className = 'inactive';

		this.tab = name;

		window.location = "#tab=" + name;
		this.url = window.location.href;
	}
});

document.observe("dom:loaded", function()
{
	var jukebox = new JukeboxView();
	jukebox.attach();
	jukebox.sync();
});
