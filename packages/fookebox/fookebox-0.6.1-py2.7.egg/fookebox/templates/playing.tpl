<div id="nowPlaying">
	<h2><img src="img/sound.png" /> ${_('Now playing')}</h2>
	<ol>
		<li id="artist"></li>
		<li id="track"></li>
		<li id="time"><span id="timePassed"></span> / <span id="timeTotal"></span></li>
% if config.get('enable_controls'):
		<li id="control">
			<a id="control-prev" href="#"><img src="img/control_prev.png" alt="back" title="${_('back')}" /></a>
			<a id="control-pause" href="#"><img src="img/control_pause.png" alt="pause" title="${_('pause')}" /></a>
			<a id="control-play" href="#"><img src="img/control_play.png" alt="play" title="${_('play')}" /></a>
			<a id="control-next" href="#"><img src="img/control_next.png" alt="next" title="${_('next')}" /></a>
			<a id="control-voldown" href="#"><img src="img/control_voldown.png" alt="volume down" title="${_('volume down')}" /></a>
			<a id="control-volup" href="#"><img src="img/control_volup.png" alt="volume up" title="${_('volume up')}" /></a>
			<a id="control-rebuild" href="#"><img src="img/control_rebuild.png" alt="rebuild database" title="${_('rebuild database')}" /></a>
		</li>
% endif
	</ol>
</div>
<div>
	<img id="nowPlayingCover" src="img/nocover.png" width="200" alt="" style="display: none" />
</div>
