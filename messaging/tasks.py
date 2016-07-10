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
from dateutil.relativedelta import relativedelta

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

@django_rq.job('email')    
def _send_mass_email(email_message, smtp_profile):
    es = SMTPHelper(smtp_profile)
    es.send_mass_email(email_message)

@django_rq.job('sms')
def _send_sms(sms_message):
    es = SMSHelper()
    es.send_sms(sms_message)

@django_rq.job('sms')   
def _send_mass_sms(sms_message):
    # params sms_message: contains all the message payload
    es = SMSHelper()
    es.send_mass_sms(sms_message)

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
    #get anniversaries that occur today
    due_public_events = PublicEvent.objects.select_related('message').filter(date = date.today())
    # For each due private anniversary,
    for publicevent in due_public_events:
        for recipient_d in publicevent.get_recipients():
            if publicevent.message.send_email and recipient_d.email and publicevent.message.email_template:
                e_msg = _compose(publicevent.message.email_template, recipient_d)
                e_title = _compose(publicevent.message.title, recipient_d)
                _send_email.delay([e_title,e_msg,recipient_d.email],publicevent.message.smtp_setting.values())
                
            if publicevent.message.send_sms and recipient_d.phone and publicevent.message.sms_template:
                s_msg = _compose(publicevent.message.sms_template, recipient_d)
                s_sender = _compose(publicevent.message.sms_sender, recipient_d)
                _send_sms.delay([s_sender,s_msg,recipient_d.phone])
            
        publicevent.update(date = date.today()+relativedelta(years=1))
    