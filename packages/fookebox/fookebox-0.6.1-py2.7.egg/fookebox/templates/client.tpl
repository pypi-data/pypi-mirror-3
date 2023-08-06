<%inherit file="base.tpl"/>

<%def name="headers()">
	<script type="text/javascript" src="js/fookebox/client.js"></script>
</%def>

<div id="message" style="display: none">
	<div class="corner tl"></div>
	<div class="corner tr"></div>
	<div class="corner bl"></div>
	<div class="corner br"></div>
	<div id="messageText"></div>
</div>
<h1 id="h1"><a href="/">${config.get('site_name')}</a></h1>
% if not config.get('hide_credits'):
<div id="meta">
	<a href="http://fookebox.googlecode.com/">fookebox</a> ${config.get('version')}<br />
	&copy; 2007-2012 <a href="http://www.ott.net/">Stefan Ott</a>
</div>
% endif
<%include file="browse-menu.tpl"/>
<div id="status">
<%include file="status.tpl"/>
</div>
<img src="img/progress.gif" alt="" id="progress" style="display: none" />
<div id="searchResult"></div>

<!-- this is a nasty hack to get our config parameters -->
<form id="config">
	<input 	type="hidden"
		name="enable_queue_album"
		value="${config.get('enable_queue_album')}"
	/>
	<input 	type="hidden"
		name="show_cover_art"
		value="${config.get('show_cover_art')}"
	/>
	<input 	type="hidden"
		name="enable_song_removal"
		value="${config.get('enable_song_removal')}"
	/>
</form>
