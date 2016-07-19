'''
Created on Jun 15, 2016

@author: Dayo
'''

from django.template import Context, Template
import logging
import django_rq
from datetime import date
from django.utils import timezone
from core.models import MessageTemplate, Event, PublicEvent, Contact, SMTPSetting
from .helper import SMTPHelper, SMSHelper
from dateutil.relativedelta import relativedelta

from .models import AdvancedMessaging, StandardMessaging, QueuedMessages, ProcessedMessages

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

@django_rq.job('email')
def _send_email(email_message, smtp_profile, **kwargs):
    es = SMTPHelper(smtp_profile)
    es.send_email(email_message, **kwargs)

@django_rq.job('email')
def _send_mass_email(email_message, smtp_profile):
    es = SMTPHelper(smtp_profile)
    es.send_mass_email(email_message)

@django_rq.job('sms')
def _send_sms(sms_message, **kwargs):
    es = SMSHelper()
    es.send_sms(sms_message, **kwargs)

@django_rq.job('sms')   
def _send_mass_sms(sms_message, **kwargs):
    # params sms_message: contains all the message payload
    es = SMSHelper()
    es.send_mass_sms(sms_message)

def process_private_anniversary():
    #get anniversaries that occur today and which have not been handled
    due_private_events = Event.objects.select_related('contact','message').filter(date__day = timezone.now().day,
                                                                      date__month = timezone.now().month,
                                                                      last_run__year__lte = timezone.now().year)
    # For each due private anniversary, prepare email and sms
    
    for peven in due_private_events:
        if peven.message.send_email and peven.contact.email and peven.message.email_template:
            etempl = _compose(peven.message.email_template, peven.contact) #compose title
            rttempl = _compose(peven.message.title, peven.contact) #compose message
            e_job = _send_email.delay([rttempl,etempl,peven.contact.email],\
                                      peven.message.smtp_setting.values(),\
                                      owner = peven.contact.kit_user
                                      )
            
        if peven.message.send_sms and peven.contact.phone and peven.message.sms_template:
            sms_msg = _compose(peven.message.sms_template, peven.contact)
            sender = _compose(peven.message.sms_sender, peven.contact)
            s_job = _send_sms.delay([sender,sms_msg,peven.contact.phone],\
                                    owner = peven.contact.kit_user
                                    )

        peven.update(last_run=timezone.now().date()) 
    
    
def process_public_anniversary():
    #get anniversaries that occur today
    due_public_events = PublicEvent.objects.select_related('message').filter(date = timezone.now().date())
    # For each due private anniversary,
    for publicevent in due_public_events:
        for recipient_d in publicevent.get_recipients():
            if publicevent.message.send_email and recipient_d.email and publicevent.message.email_template:
                e_msg = _compose(publicevent.message.email_template, recipient_d)
                e_title = _compose(publicevent.message.title, recipient_d)
                _send_email.delay([e_title,e_msg,recipient_d.email],\
                                  publicevent.message.smtp_setting.values(),\
                                  owner = publicevent.kit_user
                                  )
                
            if publicevent.message.send_sms and recipient_d.phone and publicevent.message.sms_template:
                s_msg = _compose(publicevent.message.sms_template, recipient_d)
                s_sender = _compose(publicevent.message.sms_sender, recipient_d)
                _send_sms.delay([s_sender,s_msg,recipient_d.phone],\
                                owner = publicevent.kit_user
                                )
            
        publicevent.update(date = timezone.now().date()+relativedelta(years=1))
    
def process_onetime_event():
    
    due_queued_messages = QueuedMessages.objects.filter(delivery_time__lte = timezone.now())
    
    for queued_message in due_queued_messages:
        recipients_qs = Contact.objects.filter(pk__in = queued_message.message.recipients)
        smtp_setting_qsv = SMTPSetting.objects.get(pk = queued_message.message.smtp_setting_id).values()
        
        for recipient_d in recipients_qs:
            if queued_message.message.send_email and recipient_d.email and queued_message.message.email_template:
                e_msg = _compose(queued_message.message.email_template, recipient_d)
                e_title = _compose(queued_message.message.title, recipient_d)
                _send_email.delay([e_title, e_msg, recipient_d.email],\
                                  smtp_setting_qsv, owner = queued_message.created_by
                                  )
                
            if queued_message.message.send_sms and recipient_d.phone and queued_message.message.sms_template:
                s_msg = _compose(queued_message.message.sms_template, recipient_d)
                s_sender = _compose(queued_message.message.title, recipient_d)
                _send_email.delay([s_sender, s_msg, recipient_d.phone],\
                                  owner = queued_message.created_by
                                  )                
        
        # create entry in processed message
        ProcessedMessages.objects.create(
            message_type = queued_message.message_type,
            message = queued_message.message,
            created_by = queued_message.created_by            
        )
        # delete queued message from queuedmessage table
        queued_message.delete()