'''
Created on Jul 9, 2016

@author: Dayo
'''
import sys, os
import requests
from dateutil.relativedelta import relativedelta

from django.utils import timezone
from django.core import mail
from django.core.mail import send_mail, EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.contrib.auth.models import User
from django.core.validators import validate_email

#from gomez.models import KITBilling
from .models import FailedEmailMessage, FailedSMSMessage, FailedSMSSystemBacklog
from core.models import KITUser, SMTPSetting, KITUBalance
from core.exceptions import *

from cacheops import cached_as
from django.apps import apps

from gomez.helper import temp_log_to_db, KITRateEngineA
from messaging.sms_counter import SMSCounter
from gomez.models import KITBilling
import smtplib

from .smsgw.smslive247 import SMSLive247Helper
from .smsgw.infobip import InfobipSMS

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
    
    def __init__(self, smtp_server_profile):
        
        self.ssp = smtp_server_profile
        self.id = getattr(self.ssp, 'id', None)
        
        self.smtp_server = getattr(self.ssp,'smtp_server', None)
        self.from_sender = getattr(self.ssp,'from_user','')
        self.smtp_port = getattr(self.ssp,'smtp_port', 25)
        self.connection_security = getattr(self.ssp,'connection_security','')
        self.smtp_user = getattr(self.ssp,'smtp_user','')
        self.smtp_password = getattr(self.ssp,'smtp_password','')
    
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
                mail.EmailMessage(
                    'This is an SMTP Test Message',
                    '''
                    This is a message to Test that your SMTP settings are working OK
                    
                    Regards,
                    In.Touch
                    ''',
                    self.smtp_user,
                    ['dayo@windom.biz'],
                    connection=smtp_connection,
                ).send()
                                
            return True
        except Exception:
            return(sys.exc_info())

    
    def send_email(self, email_message, **kwargs):
        
        try:
            conn = self.get_connection() 
            
            with conn as smtp_connection:    
                msg = EmailMessage(
                    subject = email_message[0], #title
                    body = email_message[1], #body
                    from_email = '"{}" <{}>'.format(self.from_sender, self.smtp_user),
                    #from_email = self.smtp_user,
                    to = [email_message[2]], #recipient
                    connection=smtp_connection,
                    #headers={'Message-ID': 'foo'},
                )
                msg.content_subtype = "html"
                msg.send()
                
                temp_log_to_db(
                    'email',
                    email_msg = email_message,
                    sender_mail = "{} <{}>".format(self.from_sender, self.smtp_user),
                    owner = kwargs['owner']
                )
        except smtplib.SMTPDataError:
            FailedEmailMessage.objects.create(
                        email_pickled_date = [email_message, self.ssp],
                        reason = str(sys.exc_info()[1]),
                        owned_by = kwargs['owner']
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
        # load us
        #get_user_balance        
        fsb = self.kuser.kitubalance.free_sms_balance
        sb = self.kuser.kitubalance.sms_balance
        
        #get sms units required to send to destination
        ppsms = KITRateEngineA().get_sms_cost_to_number(self.destination)
        
        
        
        #sms pages     
        smsct = SMSCounter().get_messages_count_only(self.sms_message)
        
        print
        # all messages are billed using the user's account balance
        if fsb >= (ppsms * smsct):
            return ['fsb', fsb-(ppsms * smsct)]
        elif sb >= (ppsms * smsct):
            return ['sb', sb-(ppsms * smsct)]
        else:
            raise NotEnoughBalanceError("Not enough units to send SMS")
        

        
        
    def _update_user_sms_balance(self, balance_acct_debited, amount):
        # save balance
        '''
        if is_company_wide(self.kuser) and self.msg_type == 'public_anniv_msg' or self.msg_type == 'private_anniv_msg':
            if balance_acct_debited == 'p_fsb':
                KITUBalance.objects.filter(kit_user=self.kuser.parent).update(free_sms_balance=amount)
            elif balance_acct_debited == 'p_sb':
                KITUBalance.objects.filter(kit_user=self.kuser.parent).update(sms_balance=amount)
        else:'''
        if balance_acct_debited == 'fsb':
            KITUBalance.objects.filter(kit_user=self.kuser).update(free_sms_balance=amount)
        elif balance_acct_debited == 'sb':
            KITUBalance.objects.filter(kit_user=self.kuser).update(sms_balance=amount)
    
    '''
    def _sms_success_logging_and_all(self, gw_id):        
        # do all logging        
        temp_log_to_db(
            'sms',
            sms_msg = [self.sender,self.sms_message,self.destination],
            message_id = self.success_message_id,
            owner = self.kuser,
            gateway_id = gw_id
        )
    
    def _sms_failure_logging_and_all(self):        
        # do all logging        
        temp_log_to_db(
            'sms',
            sms_msg = [self.sender,self.sms_message,self.destination],
            message_err_code = self.error_code,
            owner = self.kuser
        )
    '''
    
    
        
    def send_my_sms(self):        
        
        try:
            
            result = self._check_sms_can_be_sent()
            # SMSLive247
            #gw_reply = SMSLive247Helper().send_sms([self.sender, self.sms_message, self.destination])
            
            
            #send sms
            InfobipSMS().send_single_advanced_sms([self.sender, self.sms_message, self.destination], \
                                                  self.kuser, batchid=self.batch_id)

            
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
            print(result[0], result[1])
            self._update_user_sms_balance(result[0], result[1])
        
        



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


