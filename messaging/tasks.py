'''
Created on Jun 15, 2016

@author: Dayo
'''

from django.template import Context, Template
import logging
import django_rq
from datetime import date
from core.models import MessageTemplate, Event, PublicEvent
from .helper import SMTPHelper, SMSHelper

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
def _send_email(email_message, smtp_profile):
    es = SMTPHelper(smtp_profile)
    es.send_email(email_message)

@django_rq.job('sms')
def _send_sms(sms_message):
    es = SMSHelper()
    es.send_sms(sms_message)

def process_private_anniversary():
    #get anniversaries that occur today and which have not been handled
    due_private_events = Event.objects.select_related('contact','message').filter(date__day = date.today().day,
                                                                      date__month = date.today().month,
                                                                      last_run__year__lte = date.today().year)
    # For each due private anniversary, prepare email and sms
    
    for peven in due_private_events:
        if peven.message.send_email and peven.contact.email and peven.message.email_template:
            etempl = _compose(peven.message.email_template, peven.contact.all())
            rttempl = _compose(peven.message.title, peven.contact.all())
            _send_email.delay([rttempl,etempl,peven.contact.email],peven.message.smtp_setting.values())
            
        if peven.message.send_sms and peven.contact.phone and peven.message.sms_template:
            sms_msg = _compose(peven.message.sms_template, peven.contact.all())
            sender = _compose(peven.message.sms_sender, peven.contact.all())
            _send_sms.delay([sender,sms_msg,peven.contact.phone])
            
        peven.update(last_run=date.today())
    
    
def process_public_anniversary():
    #get anniversaries that occur today and which have not been handled
    due_public_events = Event.objects.filter(date__day = date.today().day,
                                              date__month = date.today().month,
                                              last_run__year__lte = date.today().year)
    # For each due private anniversary, 
    