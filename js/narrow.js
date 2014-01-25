$(document).ready(function() {
	$('img').click(function() {
		var iconId = $(this).attr('id');

		$(document).scrollTo(".featurette-divider#"+iconId, 500);
	});
	$('.glyphicon-chevron-up').click(function() {
		$(document).scrollTo(".nav", 500);
	});
	
	
});

