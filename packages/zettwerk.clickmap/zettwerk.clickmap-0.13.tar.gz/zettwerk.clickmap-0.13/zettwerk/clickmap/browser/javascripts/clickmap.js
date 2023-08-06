(function(jq) { 
    jq.fn.saveClicks = function() {
	jq(this).bind('mousedown.clickmap', function(evt) {
	    var data = collectClickerData(evt);
	    jq.post(clickmap_tool_url+'/clicker', {
		'x:int': data['x'],
		'y:int': data['y'],
		'w:int': data['w'],
		'uid': clickmap_uid
	    });
	});
    }; 
    
    jq.fn.stopSaveClicks = function() {
	jq(this).unbind('mousedown.clickmap');
    };
})(jQuery); 

function collectClickerData(evt) {
    /* 
       collect the values, needed for the clicker call.
       x: is the x position of the click relative from #visual-portal-wrapper
       y: is the y position of the click relative from #visual-portal-wrapper
       w: is the witdh (inclusive paddings and borders) from #visual-portal-wrapper
     */
    var visual_reference = getVisualReference();
    return {'x': parseInt(evt.pageX - visual_reference.offset()['left']),
	    'y': parseInt(evt.pageY - visual_reference.offset()['top']),
	    'w': visual_reference.outerWidth()};
}

function getVisualReference() {
    /* all used coordinates are relative to a reference. */
    return jq('#visual-portal-wrapper');
}

function showClickmapOutput() {
    var visual_reference = getVisualReference();
    visual_reference.width(clickmap_output_width); // make the coords suitable
    
    var src = clickmap_tool_url+'/drawImage';
    src += '?uid='+clickmap_uid;
    
    var pos = visual_reference.offset();
    var styles = 'z-index: 100; left: '+pos['left']+'px; top: '+pos['top']+'px;';
    styles += 'position: absolute; background-color: silver; display: none; border: 1px solid red';
    var output_image_tag = '<img src="'+src+'" width="'+visual_reference.outerWidth()+'" />';

    var controller_styles = 'z-index: 101; left: 300px; top: 0px; width: 300px; height=100px; padding: 3px; ';
    controller_styles += 'position: absolute; background-color: silver; border: 1px solid orange';
    var output_controller = '<div style="'+controller_styles+'" id="clickmap_output_controller"></div>';
    visual_reference.append('<div style="'+styles+'" id="clickmap_output">'+output_image_tag+output_controller+'</div>');

    jq('#clickmap_output').fadeTo('slow', 
				  0.0, 
				  function() { jq(this).show(); }
				  );
    jq('#clickmap_output').fadeTo('slow', 0.63);

    jq('#clickmap_output_controller').load(clickmap_tool_url+'/getControlPanel', {}, enableControlPanelForm);
}

function enableControlPanelForm() {
    jq('#clickmap_output_controller_form input[name=refresh]').click(function() {
	var start = jq('#clickmap_output_controller_form input[name=start]').val();
	var end = jq('#clickmap_output_controller_form input[name=end]').val();
	
	if (start && end) {
	    var new_src = clickmap_tool_url+'/drawImage?uid='+clickmap_uid+'&start='+start+'&end='+end;
	    
	    jq('#clickmap_output').fadeTo('fast', 0.0);
	    jq('#clickmap_output img').attr('src', new_src);
	    jq('#clickmap_output').fadeTo('slow', 0.63);
	} else {
	    alert ("Please enter some date");
	}
	return false;
    });
}

function clickmapSetup() {
    /* 
       we resize the windows viewport to check if the visual reference resizes also.
       If so, then the page has a variable width and the right_align_threshold must be set.
       Otherwise, the page uses a fixed width and the threshold must not be set.
     */

    var current_window_width = window.outerWidth;
    var visual_reference = getVisualReference();
    var current_visual_reference_width = visual_reference.outerWidth();

    window.resizeTo(current_visual_reference_width + 10,
		    window.outerHeight);
    var is_constant_layout = current_visual_reference_width == visual_reference.outerWidth();
    window.resizeTo(current_window_width,
		    window.outerHeight);

    jq('#form\\.output_width').val(visual_reference.outerWidth());
    jq('#form\\.output_height').val(window.outerHeight);

    if (is_constant_layout) {
	jq('#form\\.right_align_threshold').val(0);	
    } else {
	jq('#form\\.right_align_threshold').val(Math.round(visual_reference.outerWidth() / 3 * 2));
    }
}

function confirmClickmapReset() {
    if (window.confirm('Are you sure?')) {
	document.location.href = clickmap_tool_url+'/initLogger?force:bool=True';
    }
}

jq(document.body).ready(function() {
    if (clickmap_uid != '') {
	if (show_clickmap_output) {
	    showClickmapOutput();
	}
	else 
	    if (clickmap_do)
		jq('#visual-portal-wrapper').saveClicks();
    }
});
