'''
Created on Jul 13, 2016

@author: Dayo
'''

import json
import datetime, pytz
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax
from django.template import Context, Template
#from django.utils.crypto import get_random_string
from django.db import transaction

from .models import Contact, SMTPSetting, StandardMessaging, QueuedMessages, AdvancedMessaging
from messaging.sms_counter import SMSCounter

from .forms import StandardMessagingForm

def _compose(template, convars):
    
    t = Template(template)
    return t.render(Context({
                            'firstname':getattr(convars,'first_name',''),
                            'lastname':getattr(convars,'last_name',''),
                            'salutation':getattr(convars,'salutation',''),
                            'email':getattr(convars,'email',''),
                            'phone':getattr(convars,'phone',''),                            
                            })
                    )


myform = None

@ajax
@login_required
def prepare_to_send_message(request):
    #c = "foo " + request.POST['recipients']
    #return {'result': c}
    global myform
    
    if request.method == 'POST':
        #return {'result':request.POST.getlist('recipients',[])}
        #get contacts

        if request.POST.get('message_type') == 'STANDARD':
            myform = StandardMessagingForm(request.POST)  
            if not myform.is_valid():
                return {'errors':myform.errors.as_json(escape_html=True)}
            else:
                recipients = request.POST.getlist('recipients',None)
                cts = Contact.objects.filter(pk__in=recipients)
                result_dict = {}
            
                #Return: "Email will be sent to (38) recipients"
                
                if request.POST.get('send_email', False):
                    #I need the number of recipients who have emails accounts registered on the system
                    num_of_contacts_with_emails = cts.exclude(email__exact='').count()
                    
                    smtp_to_use = SMTPSetting.objects.get(pk=request.POST.get('smtp_setting',''))
                    
                    result_dict['nocwe'] = num_of_contacts_with_emails
                    result_dict['mail_server'] = '<a href="{}" target="_blank">{}</a>'.\
                                                format(smtp_to_use.get_absolute_url(),smtp_to_use.smtp_server)            
                    result_dict['sample_email'] = _compose(request.POST.get('email_message'),cts.first()) #convert to img
                    result_dict['sample_email_title'] = _compose(request.POST.get('title'),cts.first())
                    #code_seg_1 = get_random_string(length=10)
                
                else:
                    result_dict['nocwe'] = 0 #if this is 0, then it all dont matter
                
                #Return: Total SMSs to be sent (200), Send Units Available (550)
                 
                if request.POST.get('send_sms', False):
                    m_count = 0
                    
                    contacts_with_phone = cts.exclude(phone__exact = '')
                    
                    for contact in contacts_with_phone:
                        mc_var = SMSCounter().get_messages_count_only(_compose(request.POST.get('sms_message'), contact))
                        m_count+=mc_var
                        
                    result_dict['total_sms_count'] = m_count
                    result_dict['sample_sms'] = _compose(request.POST.get('sms_message'),cts.first())
                    #code_seg_2 = get_random_string(length=10)
                    
                else:
                    result_dict['total_sms_count'] = 0
                
                #result_dict['idtdt'] = idondit = "{}{}".format(code_seg_1, code_seg_2)       
                return {'result':result_dict}
                
    

@ajax
@login_required
@transaction.atomic
def send_message(request):
    
    global myform
    
    if request.method == 'POST':
        
        # remove message from draft if it has been drafted
        if request.POST.get("message_type") == 'STANDARD':
            #delete item from draft
            if StandardMessaging.objects.filter(pk = request.POST.get('message_id'), created_by = request.user.kituser).exists():
                print("exists")
            
            # send message to queue table
            QueuedMessages.objects.create(
                message_type = request.POST.get("message_type"),
                message_id = request.POST.get("message_id",0), #-1 means it was never saved to draft
                message = {
                    'title':myform.cleaned_data.get('title',''),
                    'email_template':myform.cleaned_data.get('email_message',''),
                    'sms_template':myform.cleaned_data.get('sms_message',''),
                    'send_email' : myform.cleaned_data.get('send_email', True),
                    'send_sms' : myform.cleaned_data.get('send_sms', True),
                    'sms_sender_id' : myform.cleaned_data.get('sms_sender',''),
                    'recipients' : request.POST.getlist('recipients',[]),
                    'smtp_setting_id': request.POST.get('smtp_setting','')
                           },
                delivery_time = timezone.make_aware(myform.cleaned_data.get('delivery_time'),timezone.get_current_timezone()),
                created_by = request.user.kituser
                
            )
            
            return {'result':'Success! Message Queued for Sending'}
            
        elif request.POST.get("message_type") == 'ADVANCED':
            pass
