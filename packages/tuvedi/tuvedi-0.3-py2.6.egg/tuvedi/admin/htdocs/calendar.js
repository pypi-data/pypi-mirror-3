$(document).ready(function() {
	$.ajax({
		url: tuvedi_cmd_url + "get-presentations",
		dataType: "json",
		success: function(data) {
			var i,e;
			var eventObject;
			for(i=0;i < data.length; i++) {
				e = $("<div class='external-event'>" + data[i]['title'] + "</div>");
				eventObject = {
					title: data[i]['title'],
					presentation_id: data[i]['id']
				}
				$('#external-events').append(e);
				$(e).data('eventObject', eventObject);

				$(e).draggable({
					zIndex: 999,
					revert: true,
					revertDuration: 0
				});
			}
		}
	});

	$('#external-events div.external-event').each(function() {
		var eventObject = {
			title: $.trim($(this).text()) // use the element's text as the event title
		};

		$(this).data('eventObject', eventObject);

		$(this).draggable({
			zIndex: 999,
			revert: true,
			revertDuration: 0
		});

	});


	/* initialize the calendar
	-----------------------------------------------------------------*/

	$('#calendar').fullCalendar({
		events: tuvedi_cmd_url + "get-timetable/" + device_id,
    slotMinutes: 5,
		eventDrop: function(event,dayDelta,minuteDelta,allDay,revertFunc) {
			//console.log("drop", event);
			event['changed'] = true;
		},
		eventResize: function(event,dayDelta,minuteDelta,revertFunc) {
			//console.log("resize", event);
			event['changed'] = true;
		},
		header: {
			left: 'prev,next today',
			center: 'title',
			right: 'month,agendaWeek,agendaDay'
		},
		editable: true,
		droppable: true, // this allows things to be dropped onto the calendar !!!
		drop: function(date, allDay) { // this function is called when something is dropped

			// retrieve the dropped element's stored Event Object
			var originalEventObject = $(this).data('eventObject');

			// we need to copy it, so that multiple events don't have a reference to the same object
			var copiedEventObject = $.extend({}, originalEventObject);

			// assign it the date that was reported
			copiedEventObject.start = date;
			copiedEventObject.allDay = allDay;

			// render the event on the calendar
			// the last `true` argument determines if the event "sticks" (http://arshaw.com/fullcalendar/docs/event_rendering/renderEvent/)
			$('#calendar').fullCalendar('renderEvent', copiedEventObject, true);

			// is the "remove after drop" checkbox checked?
			if ($('#drop-remove').is(':checked')) {
				// if so, remove the element from the "Draggable Events" list
				$(this).remove();
			}

		}
	});


});

function extract_values(e, values) {
	var i;
	tmp_event = {}
	for(i=0; i < values.length; i++) {
		if(values[i] == "end" || values[i] == "start") {
			//console.log(e[values[i]]);
			tmp_event[values[i]]=$.fullCalendar.formatDate(e[values[i]], "yyyy-MM-dd HH:mm");
		} else {
			tmp_event[values[i]]=e[values[i]];
		}
	}
	return tmp_event;
}
function test() {
	// must be global
	events_update = [];
	var events_new = [];
	var events_delete = [];
	events = $("#calendar").fullCalendar( 'clientEvents');
	for(i=0; i < events.length; i++) {
		//console.log(events[i]);
		if(events[i]['id'] === undefined) {
			events_new.push(extract_values(events[i],['start','end', 'allDay','presentation_id']));
		} else if(events[i]['changed'] !== undefined) {
			events_update.push(extract_values(events[i],['start','end', 'allDay','id']));
		}
	}
	$.post(
		tuvedi_cmd_url + "set-timetable/" + device_id,
		{
			d: JSON.stringify({
				insert: events_new,
				update: events_update
			})
		}
	);
	//console.log(events_new, events_update, events_delete);
}
