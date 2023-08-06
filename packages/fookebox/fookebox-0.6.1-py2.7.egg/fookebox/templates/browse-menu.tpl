<div id="browse-menu">
	<ul id="selectType">
		<li id="artistTab" class="active"><a href="#tab=artist">${_('Artists')}</a></li>
		<li id="genreTab" class="inactive"><a href="#tab=genre">${_('Genres')}</a></li>
% if config.get('show_search_tab'):
		<li id="searchTab" class="inactive"><a href="#tab=search">${_('Search')}</a></li>
% endif
	</ul>
	<div id="artistList">
		<div id="letterSelector">
% for char in range(ord('A'), ord('Z') + 1):
<%	key = chr(char) %>
			<a href="#${key}">${key}</a>
% endfor
		</div>
		<ul>
<%
	prev = ''
	char = ''
%>
% for artist in artists:
% 	if len(artist.name) > 0:
<%		char = artist.name[0].upper() %>
%	endif
%	if prev != char:
			<li class="seperator">
				<a href="#artist=${artist.base64}" name="${char}" id="artist-${artist.base64}" class="artistLink">${artist.name}</a>
%	else:
			<li>
%		if len(artist.name) > 0:
				<a href="#artist=${artist.base64}" id="artist-${artist.base64}" class="artistLink">${artist.name}</a>
%		else:
				<a href="#artist=${artist.base64}" id="artist-${artist.base64}" class="artistLink">${_('(none)')}</a>
%		endif
%	endif
			</li>
%	if len(artist.name) > 0:
<%		prev = char %>
%	endif
% endfor
		</ul>
	</div>
	<ul id="genreList" style="display: none">
% for genre in genres:
% if genre.name != '':
		<li><a href="#genre=${genre.base64}" id="genre-${genre.base64}" class="genreLink">${genre.name}</a></li>
% else:
		<li><a href="#genre=${genre.base64}" id="genre-${genre.base64}" class="genreLink">${_('(none)')}</a></li>
% endif
% endfor
	</ul>
% if config.get('show_search_tab'):
	<ul id="searchList" style="display: none">
		<form id="searchForm" name="searchform" action="">
			<select name="searchType">
				<option selected value="artist">${_('Artist')}</option>
				<option value="album">${_('Album')}</option>
				<option value="title">${_('Title')}</option>
				<option value="filename">${_('Filename')}</option>
				<option value="any">${_('Any')}</option>
			</select>
			<input type="text" name="searchTerm" />
			<input type="submit" value="Search!">
		</form>
	</ul>
% endif
</div>
