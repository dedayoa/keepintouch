/**
 * 
 */

$( document ).ready(function() {
	$('.event-form-date').fdatepicker({
		/*initialDate: '02-12-1989',*/
		format: 'dd-mm-yyyy',
		disableDblClickSelection: true
	});
	
	$('.django-select2').djangoSelect2();
});