% for event in events:
		<tr id="event-${event.id}"
% if event == current:
			class="currentEvent"
% endif
		>
			<td>
% if edit == event.id:
				<form method="post" action="schedule">
				<input type="hidden" name="id" value="${event.id}" />
				<input name="hour" size="2" value="${"%02d" % event.time.hour}" />:<input name="minute" size="2" value="${"%02d" % event.time.minute}" />
% else:
				${event.time.strftime('%H:%M')}
			</td>
% endif
			<td>
% if edit == event.id:
				<input name="name" value="${event.name}" />
% else:
				${event.name}
% endif
			</td>
			<td>
% if edit == event.id:
				<select name="type">
% for type in range(0, 3):
						<option value="${type}"
% if event.type == type:
						selected="selected"
% endif
						>${h.event_type_name(type)}</option>
% endfor
				</select>
% else:
				${h.event_type_name(event.type)}
% endif
			</td>
			<td>
% if edit == event.id:
				<input type="submit" />
				<input type="button" value="abort" onclick="window.location='schedule'; return false" />
			</form>
% else:
				<a href="schedule?edit=${event.id}"><img src="img/edit.png" alt="edit" title="Edit this event" /></a>
% if event != current:
% if event != events[len(events) - 1]:
				<a href="#" onclick="prog.moveDown('${event.id}'); return false"><img src="img/arrow_down.png" alt="down" title="Move this event down in the schedule" /></a>
% endif
% if event != events[0]:
<a href="#" onclick="prog.moveUp('${event.id}'); return false"><img src="img/arrow_up.png" alt="up" title="Move this event up in the schedule" /></a>
% endif
				<a href="#" onclick="prog.setCurrent('${event.id}'); return false"><img src="img/setcurrentevent.png" alt="set current" title="Set as current event" /></a>
				<a href="#" onclick="prog.remove('${event.id}'); return false"><img src="img/delete.png" alt="delete" title="Delete this event" /></a>
% endif
			</td>
% endif
		</tr>
% endfor
