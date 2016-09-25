/**
 * 
 */


$(document).foundation();

if ($('#id_all_contacts').prop('checked')){
	$('#div_id_recipients').hide()
}else{
	$('#div_id_recipients').show()
}


function get_u_val(valu){
	// returns 'Yes' or 'No', instead of Blank or true
	if (valu == true){
		return 'Yes';
	}
	else{
		return 'No';
	}
};

function get_tpl_vars(text){
	//returns an array of tpl vars 
	var re = /{{\w+}}/g;
	var m;
	var n = new Array();
	do{
		m = re.exec(text);
		if (m){
			n.push(m[0]);
		}
	}while(m);
	
	return n;
};

function enset_tpl_vars(args){
	// returns a set of the items in the arrays passed as args
	var args_set = new Set();
	for (idx1 in args){
		for (item in args[idx1]){
			args_set.add(args[idx1][item]);
		}
	}
	return args_set;
}


function sayconnectiondown(){
	Offline.check();
    if (Offline.state === 'down'){
    	Offline.check();
    }
    else{    	
    	return;
    }
}

var loading = $('#loadingDiv').hide();

$(document)
  .ajaxStart(function () {
    loading.show();
  })
  .ajaxStop(function () {
    loading.hide();
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

$(document).click(function() {
	$('div#k-dropdown-content').hide();
});

// set margin as window is resized to take care of media queries reducing/increasing the size of headers
// and therefore distorting the right edge of the divs
$(window).resize(function() {
	var kupn_width = $("#k-user-profile-nav").width()/parseFloat($("body").css("font-size")); //width in rem
	var kdc_width = $("#k-dropdown-content").width()/parseFloat($("body").css("font-size"));
	$("#k-dropdown-content").css("margin-left",kupn_width-kdc_width+"rem");
});

$(document).ready(function(){
	
	$('a#k-user-greeting').click(function(e){
		e.stopPropagation();
		$('div#k-dropdown-content').toggle(0);
	})
	
	
	$("a.isfb-link").click(function(e){
		var brm = new Foundation.Reveal($("#bug-report-modal"));
		brm.open();
	})
	
	var kupn_width = $("#k-user-profile-nav").width()/parseFloat($("body").css("font-size")); //width in rem
	var kdc_width = $("#k-dropdown-content").width()/parseFloat($("body").css("font-size"));
	$("#k-dropdown-content").css("margin-left",kupn_width-kdc_width+"rem");
	
	
	$("form#issue-submit-form").submit(function(e){
		
		
		e.preventDefault();
		
		var payload = new FormData(this);	
		ajaxPost('/messaging/system/feedback/', payload, function(content){
			
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