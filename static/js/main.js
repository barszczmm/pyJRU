function helpContainers() {
	$('.help').hide().before('<div class="help-icon">?</div>');
	$('.help-icon').click(
		function() {
			var $help = $(this).next('.help');
			if ($help.is(':visible')) {
				$help.slideUp();
			} else {
				$help.slideDown();
			}
				
		}
	);
}

function cautionContainers() {
	$('.caution').show().before('<div class="caution-icon">!</div>');
	$('.caution-icon').click(
		function() {
			var $caution = $(this).next('.caution');
			if ($caution.is(':visible')) {
				$caution.animate({height: 'hide'});
			} else {
				$caution.animate({height: 'show'});
			}
				
		}
	);
}

function helpAndCaution() {
	helpContainers()
	cautionContainers();
}

function formHandler() {
	$('form input[type="submit"]').click(
		function() {
			var $form = $(this).parents('form'),
				data = {},
				$overlay = $('<div class="form-overlay"><span class="text">processing...</span></div>'),
				$errors = $('.errors', $form);
			
			$form.append($overlay.css('opacity', 0.7));
			data[$(this).attr('name')] = $(this).val();
			$('input:not([type="submit"]), textarea', $form).each(
				function() {
					data[$(this).attr('name')] = $(this).val();
				}
			);
			$.ajax({
				type: 'POST',
				url: $form.attr('action'),
				data: data,
				success: function(data, textStatus, jqXHR) {
					$('.result textarea').val(data);
					$overlay.fadeOut().remove();
					if ($errors.length) {
						$errors.remove();
					}
				},
				error: function(jqXHR, textStatus, errorThrown) {
					if ($errors.length) {
						$errors.html(jqXHR.responseText);
					} else {
						$errors = $('<p class="errors">' + jqXHR.responseText + '</p>');
						$('.basic', $form).before($errors);
					}
					$overlay.fadeOut().remove();
				}
			});
			return false;
		}
	);
}

$(document).ready(function() {
	
	helpAndCaution();

	formHandler();

});