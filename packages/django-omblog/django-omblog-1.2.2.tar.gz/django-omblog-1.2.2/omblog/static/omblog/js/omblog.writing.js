/*
	js to turn your average run of the mill textarea
	into a delicious writing experience.
	
	The "Pencil" icon from the Noun Project 
	http://thenounproject.com/noun/pencil/#icon-No347
	is used under a http://creativecommons.org/licenses/by/3.0/
	license.
	
*/

django.jQuery(function($){

	var activate_link 		= $('<a>').addClass('activate');
	var deactivate_link 	= $('<a>').addClass('deactivate');
	var ajax_progress 		= $('<a>').addClass('ajax_progress')
									.text('Saving')
									.hide();
	var original_width 		= $('#id_source_content').width();
	var original_height 	= $('#id_source_content').height();

	activate = function(){
		var width = $(document).width();
		var height = $(document).height();
		var stateObj = {writing: true};
		$('#id_source_content')
			.focus()
			.parent()
				.addClass('writing')
				.height(height)
				.width(width)
			.find('textarea')
				.height(height);
	}

	deactivate = function(){
		$('#id_source_content')
			.parent()
				.removeClass('writing')
				.height('auto')
				.width('auto')
			.find('textarea')
				.height(original_height)
				.width(original_width);
	}

	submit = function(){
				$('a.ajax_progress').show();
				$('#id_tags_to option').each(function(){
					$(this).attr('selected', 'selected');
				})
				data = $('#content-main form').serialize();
				$.ajax({
				  type: 'POST',
				  url: window.location.href,
				  data: data,
					success : function(){
						$('a.ajax_progress').fadeOut(200)
					}
				});
			}

	activate_link.click(activate)

	$('#id_source_content')
		.after(activate_link)
		.after(deactivate_link)
		.after(ajax_progress)

	deactivate_link.click(deactivate)

	$(document).keydown(function(event) {
		console.log(event.metaKey)
		console.log(event.which)
		if (!( String.fromCharCode(event.which).toLowerCase() == 's' && event.metaKey) && !(event.which == 19)) return true;
			submit();
			event.preventDefault();
			return false;
		});

	$(window).keyup(function(e) {
	  if (e.keyCode == 27) { deactivate() }   // esc
	});
	
	$(window).resize(function(){
		var width = $(window).width();
		var height = $(window).height();
		console.log(width)
		$('div.writing')
			.width(width)
			.height(height)
	})
})

