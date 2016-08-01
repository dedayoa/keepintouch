/**
 * 
 */
$(document).foundation();

if ($('#id_all_contacts').prop('checked')){
	$('#div_id_recipients').hide()
}else{
	$('#div_id_recipients').show()
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
		}, {"processData":false,"contentType":false,"cache":false});
		
	})
});