'''
Created on Jul 9, 2016

@author: Dayo
'''

import json
import sys, os
import re
import requests
from dateutil.relativedelta import relativedelta
from django.template import Context, Template, loader

from django.utils import timezone
from django.core import mail
from django.core.mail import send_mail, EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.contrib.auth.models import User
from django.core.validators import validate_email

#from gomez.models import KITBilling
from .models import FailedEmailMessage, FailedSMSMessage, FailedSMSSystemBacklog
from core.models import KITUser, SMTPSetting, KITUBalance, Contact
from core.exceptions import *

from cacheops import cached_as
from django.apps import apps

from gomez.helper import temp_log_to_db, KITRateEngineA
from messaging.sms_counter import SMSCounter
from gomez.models import KITBilling
import smtplib

from .smsgw.smslive247 import SMSLive247Helper
from .smsgw.infobip import InfobipSMS

import phonenumbers
from reportng.models import EmailDeliveryReport

#@cached_as(KITBilling, KITUser, timeout=4*3600)        
def is_company_wide(kuser):
    try:
        if kuser.is_admin:
            raise FailedSendingMessageError("Admin User Cannot Send Messages")
        elif not kuser.is_admin:
            return kuser.parent.kitsystem.company_wide_contacts
    except AttributeError:
        # this is here to take care of system which has no parent
        return False


class SMTPHelper():
    
    def __init__(self, smtp_server_profile, email_message, batch_id, **kwargs):
        
        self.ssp = smtp_server_profile
        self.id = getattr(self.ssp, 'id', None)
        
        self.smtp_server = getattr(self.ssp,'smtp_server', None)
        self.from_sender = getattr(self.ssp,'from_user','')
        self.smtp_port = getattr(self.ssp,'smtp_port', 25)
        self.connection_security = getattr(self.ssp,'connection_security','')
        self.smtp_user = getattr(self.ssp,'smtp_user','')
        self.smtp_password = getattr(self.ssp,'smtp_password','')
        
        self.reply_to = kwargs.get('reply_to')
        
        self.email_title = email_message[0]
        self.email_msg = email_message[1]
        self.email_recipient = email_message[2]
        self.email_cc_recipients = kwargs.get('cc_recipients')
        
        self.kuser = kwargs.get('owner')
        
        self.batch_id = batch_id
        
    
    # will need to cache this later
    def get_connection(self):
        
        @cached_as(SMTPSetting.objects.filter(pk=self.id), timeout=3600)
        def _get_connection():
            
            if self.connection_security == 'SSLTLS':
                connection = mail.get_connection(
                        host = self.smtp_server,
                        port = self.smtp_port,
                        username = self.smtp_user,
                        password = self.smtp_password,
                        use_ssl = True,
                        timeout=30
                        )
                return connection
            
            elif self.connection_security == 'STARTTLS':
                connection = mail.get_connection(
                        host = self.smtp_server,
                        port = self.smtp_port,
                        username = self.smtp_user,
                        password = self.smtp_password,
                        use_tls = True,
                        timeout=30
                        )
                return connection
            
            else:
                connection = mail.get_connection(
                        host = self.smtp_server,
                        port = self.smtp_port,
                        username = self.smtp_user,
                        password = self.smtp_password,
                        timeout=30
                        )
                return connection
        
        return _get_connection()
    
    
            
    def test_smtp_server(self, **kwargs):
        
        try:
            
            conn = self.get_connection()
            
            with conn as smtp_connection:
                EmailMessage(
                    subject = self.email_title,
                    body = self.email_msg,
                    from_email = self.smtp_user,
                    to = [self.email_recipient],
                    connection=smtp_connection,
                ).send()
                                
            return True
        except Exception:
            return(sys.exc_info())

    
    def send_email(self):
        
        try:
            conn = self.get_connection() 
            
            # create delivery report to get email_uuid to use to track email
            email_uuid = EmailDeliveryReport.objects.create(
                    batch_id = self.batch_id,
                    to_email = self.email_recipient,
                    from_email = self.smtp_user,
                    email_message = {
                                     'title':self.email_title,
                                     'from' : self.smtp_user,
                                     'to' : self.email_recipient,
                                     'cc' : self.email_cc_recipients,
                                     'reply_to' : self.reply_to,
                                     'message' : self.email_msg
                                     },
                    email_gateway = {
                            'server' :self.smtp_server,
                            'port': self.smtp_port,
                            'security': self.connection_security,
                            'username' : self.smtp_user
                                     },
                    msg_status = '6',
                    kituser_id = self.kuser.id,
                    kitu_parent_id = self.kuser.get_parent().id
            )
            
            with conn as smtp_connection:    
                msg = EmailMessage(
                    subject = self.email_title, #title
                    body = self.email_msg, #body
                    from_email = '"{}" <{}>'.format(self.from_sender, self.smtp_user),
                    #from_email = self.smtp_user,
                    to = [self.email_recipient], #recipient
                    cc = self.email_cc_recipients,
                    reply_to = self.reply_to,
                    connection=smtp_connection,
                    headers={
                            'X-Mailer': 'In.Touch Business Communication Automation',
                            'X-Twitter-ID': '@intouchng',
                            'X-Facebook-ID' : 'https://www.facebook.com/intouchng',
                            "X-SMTPAPI": json.dumps({
                                            "unique_args": {
                                                "batch_id" : str(self.batch_id),
                                                'email_id' : str(email_uuid.id)
                                            }
                                        })
                             },
                )
                msg.content_subtype = "html"
                msg.send()
                
                
        except smtplib.SMTPDataError:
            FailedEmailMessage.objects.create(
                        email_pickled_date = [self.email_msg, self.ssp],
                        reason = str(sys.exc_info()[1]),
                        owned_by = self.kuser
                                              )

#todo :

class SMSHelper():
    
    def __init__(self, message, kuser, msg_type, batch_id=''):
        
        self.message = message
        self.sender = self.message[0]
        self.destination = self.message[2]
        self.sms_message = self.message[1]
        self.kuser = kuser
        self.msg_type = msg_type
        self.batch_id = batch_id #this is the id for messages with multi recipients, processed in batches
        
        self.error_code = ""
        self.success_message_id = ""
        
    def _check_sms_can_be_sent(self):
        
        # check there is a destination
        if self.destination == "":
            raise InvalidPhoneNumberError("Recipient Number Not Provided")
        
        # check that phone number is valid        
        if not phonenumbers.is_valid_number(phonenumbers.parse(self.destination)):
            raise InvalidPhoneNumberError("%s is Not a Valid Phone Number"%str(self.destination))
        
        # check that user has enough SMS balance to send message
        #get_user_balance        
        user_balance = self.kuser.kitubalance.user_balance
                
        #get sms units required to send to destination
        ppsms = KITRateEngineA().get_sms_cost_to_number(self.destination)
        
        #sms pages     
        smsct = SMSCounter().get_messages_count_only(self.sms_message)
        
        # all messages are billed using the user's account balance
        if user_balance >= (ppsms * smsct):
            return user_balance-(ppsms * smsct)
        else:
            raise NotEnoughBalanceError("Not enough units to send SMS")
        

        
        
    def _update_user_account_balance(self, amount):
        # save balance
        KITUBalance.objects.filter(kit_user=self.kuser).update(user_balance=amount)
    
    
        
    def send_my_sms(self):        
        
        try:
            
            result = self._check_sms_can_be_sent()
            # SMSLive247
            #gw_reply = SMSLive247Helper().send_sms([self.sender, self.sms_message, self.destination])
            
            
            #send sms
            InfobipSMS().send_single_advanced_sms([self.sender, self.sms_message, self.destination], \
                                                  self.kuser, batchid=self.batch_id)
        
        
        except InvalidPhoneNumberError as e:
            FailedSMSMessage.objects.create(
                        sms_pickled_data = self.message,
                        reason = e.message,
                        owned_by = self.kuser,
                        batch_id = self.batch_id
                                            )
            
        except NotEnoughBalanceError as e:
            # saved message to failed table for user
            FailedSMSMessage.objects.create(
                        sms_pickled_data = self.message,
                        reason = e.message,
                        owned_by = self.kuser,
                        batch_id = self.batch_id
                                            )
        except SMSGatewayError as e:
            # admin to handle SMSGW error...log this, alert...do something!!
            FailedSMSSystemBacklog.objects.create(
                        sms_pickled_data = self.message,
                        reason = e.message,
                        owned_by = self.kuser,
                        batch_id = self.batch_id                       
                        )
        except MissingSMSRateError as e:
            FailedSMSSystemBacklog.objects.create(
                        sms_pickled_data = self.message,
                        reason = e.message,
                        owned_by = self.kuser,
                        batch_id = self.batch_id                        
                        )
        else:
            # sms successfully sent...no exception. Deduct balance
            self._update_user_account_balance(result)
        
        



class OKToSend(object):
    # used in place of the initial ok_to_send to cater for Free Users
    
    def __init__(self, kuser):
        self.user = kuser.user
        self.owner = kuser

        
    def _is_active(self):
        if self.owner.is_admin:
            raise FailedSendingMessageError("Admin User Cannot Send Messages")
        else:
            if self.user.is_active and self.owner.parent.user.is_active:
                return True            
            elif self.user.is_active == False:
                raise IsNotActiveError("User is not active")
            elif self.owner.parent.user.is_active == False:
                raise IsNotActiveError("Parent is not active")
        
            
    def _has_valid_subscription(self):
        if self.owner.is_admin:
            raise FailedSendingMessageError("Admin User Cannot Send Messages")
        else:
            if self.owner.parent.kitbilling.next_due_date >= timezone.now().date():
                return True
            else:
                raise NoActiveSubscriptionError("Admin Subscription has expired")
    
    
       
    def check(self):
        return (self._is_active() and self._has_valid_subscription())
   
    
def get_next_delivery_time(repeat_frequency, delivery_time):
    if repeat_frequency == "norepeat":
        return delivery_time
    elif repeat_frequency == "hourly":
        return delivery_time+relativedelta(hours=1)
    elif repeat_frequency == "daily":
        return delivery_time+relativedelta(days=1)
    elif repeat_frequency == "weekly":
        return delivery_time+relativedelta(weeks=1)
    elif repeat_frequency == "monthly":
        return delivery_time+relativedelta(months=1)
    elif repeat_frequency == "quarterly":
        return delivery_time+relativedelta(months=3)
    elif repeat_frequency == "annually":
        return delivery_time+relativedelta(years=1) 




def assemble_message(template_file, convars, custom_convars = {}):
    # This composes the message using the template and the context variables
    # users cannot override the default_convars for contacts
    
    t = loader.get_template(template_file)
    context_vars = custom_convars 
    
    default_convars = {
                        'firstname':getattr(convars,'first_name',''),
                        'lastname':getattr(convars,'last_name',''),
                        'salutation':getattr(convars,'salutation',''),
                        'email':getattr(convars,'email',''),
                        'phone':getattr(convars,'phone',''),                            
                        }
    context_vars.update(default_convars)
    
    return t.render(Context(context_vars))




    
def text_2_wordlist(text, max_number_of_words):
    text_list = re.sub("[^\w]", " ",  text).split()
    return " ".join(text_list[0:max_number_of_words])+"..." if len(text_list) > max_number_of_words else text


def templatesyntaxerror_message(msg):
    # returns a more (In.Touch) useful TemplateSyntaxError message
    res0 = re.search("'\w+ \w+'",str(msg))
    if res0:
        res1 = res0.group(0)
        return "The placeholder {{{{{0}}}}} is Invalid".format(res1[1:-1])
    
    
    
def contactpklist_to_emaillist(contactpklist):
    
    elist = []
    
    for el in contactpklist:
        elist.append(Contact.objects.get(pk=el).email)
        
    return elist