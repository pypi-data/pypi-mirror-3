<div id="playlist">
	<h2><img src="img/queue.png" /> ${_('Queue')}</h2>
	<ol>
% for i in range(0, int(config.get('max_queue_length'))):
		<li>&nbsp;</li>
% endfor
	</ol>
</div>
