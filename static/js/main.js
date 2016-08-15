/**
 * 
 */
$(document).foundation();

if ($('#id_all_contacts').prop('checked')){
	$('#div_id_recipients').hide()
}else{
	$('#div_id_recipients').show()
}


var $loading = $('#loadingDiv').hide();

$(document)
  .ajaxStart(function () {
    $loading.show();
  })
  .ajaxStop(function () {
    $loading.hide();
  });

jQuery.fn.highlight = function () {
    $(this).each(function () {
        var el = $(this);
        $("<div/>")
        .width(el.outerWidth())
        .height(el.outerHeight())
        .css({
            "position": "absolute",
            "left": el.offset().left,
            "top": el.offset().top,
            "background-color": "#ffff99",
            "opacity": ".7",
            "z-index": "9999999"
        }).appendTo('body').fadeOut(2000).queue(function () { $(this).remove(); });
    });
}

$(document).ready(function(){
	$("a.isfb-link").click(function(e){
		var brm = new Foundation.Reveal($("#bug-report-modal"));
		brm.open();
	})
	
	$("form#issue-submit-form").submit(function(e){
		
		
		e.preventDefault();
		
		var payload = new FormData(this);	
		ajaxPost('/settings/system/feedback/', payload, function(content){
			
			if (content.hasOwnProperty("errors")){
       			var errors = $.parseJSON(content.errors);	
       		
       			$.each(errors, function(index, value){
       				if (index === '__all__'){
       					$('div.nonfield-ajax-error').remove();
       					$("small.error").remove();
       					$("#sms-transfer-form").prepend('<div class="alert callout nonfield-ajax-error">'+value[0].message+'</div>');
       				}else{
       					$("small.error").remove();
       					//select field with error and apply text after it
       					$("[name="+index+"]").after('<small class="error">'+value[0].message+'</small>');
       				}
       			});
       			
       			return;
       			
       		}else{
       			$('div.nonfield-ajax-error').remove();
       			$("small.error").remove();
       			
       			console.log(content.result);
       			
       			//document.getElementById("issue-submit-form").reset();
       			$("#issue-submit-form")[0].reset();
       			var brtu = new Foundation.Reveal($("#bug-report-thankyou"));
       			$("#bug-report-modal").foundation('close');
				setTimeout(brtu.open(),1000);
				
       		}
		}, {contentType:false,processData:false,cache:false});
		
	});
});