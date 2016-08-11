'''
Created on Jul 9, 2016

@author: Dayo
'''
import sys
import requests
from dateutil.relativedelta import relativedelta

from django.utils import timezone

from django.core import mail
from django.core.mail import send_mail, EmailMessage
from django.core.mail.backends.smtp import EmailBackend

from django.core.validators import validate_email
from .models import SMSReport, EmailReport
from core.models import KITUser





def temp_log_to_db(m_type, **kwargs):
    
    if m_type == 'email':
        EmailReport.objects.create(
            to_email = kwargs['email_msg'][2],
            from_email = kwargs['sender_mail'],
            status = 0,
            owner = kwargs['owner'],
            email_message = {
                'title' : kwargs['email_msg'][0],
                'body' : kwargs['email_msg'][1]
                           },
            email_gateway = {
                'email_id' :'',
                'gateway_id' : '',
                'gateway_error_preamble' : kwargs['gw_err_preamble']
                
                           }
        )
    
    if m_type == 'sms':
        SMSReport.objects.create(
            to_phone = kwargs['sms_msg'][2],
            status = 0,
            owner = kwargs['owner'],
            sms_message = {
                'sender_id' : kwargs['sms_msg'][0],
                'body' : kwargs['sms_msg'][1],
                'message_type' : '0'
                           },
            sms_gateway = {
                'message_id' : kwargs['message_id'],
                'gateway_id' : '',
                'gateway_error_code' : kwargs['gw_err_code']
                           },
        )
    
    
    


class SMTPHelper():
    
    def __init__(self, smtp_server_profile):
        
        self.smtp_server = getattr(smtp_server_profile,'smtp_server',None)
        self.from_sender = getattr(smtp_server_profile,'from_user','')
        self.smtp_port = getattr(smtp_server_profile,'smtp_port',25)
        self.connection_security = getattr(smtp_server_profile,'connection_security','')
        self.smtp_user = getattr(smtp_server_profile,'smtp_user','')
        self.smtp_password = getattr(smtp_server_profile,'smtp_password','')
    
    # will need to cache this later
    def _get_connection(self):
        
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
            
    def test_smtp_server(self, **kwargs):
        
        try:
            
            conn = self._get_connection()                 
            
            with conn as smtp_connection:
                mail.EmailMessage(
                    'Test Email from IntouchNG',
                    'This is a test email to check your SMTP setup',
                    self.smtp_user,
                    ['system-notification@intouchng.com'],
                    connection=smtp_connection,
                ).send()
                                
            return True
        except Exception:
            return(sys.exc_info())

    
    def send_email(self, email_message, **kwargs):
        
        try:
            conn = self._get_connection() 
            
            with conn as smtp_connection:    
                msg = EmailMessage(
                    subject = email_message[0], #title
                    body = email_message[1], #body
                    from_email = "{} <{}>".format(self.from_sender, self.smtp_user),
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
        except Exception:
            temp_log_to_db(
                'email',
                email_msg = email_message,
                gw_err_preamble = str(sys.exc_info()),
                sender_mail = "{} <{}>".format(self.from_sender, self.smtp_user),
                owner = kwargs['owner']
            )
            return(sys.exc_info())

#todo :

class SMSHelper():
    
    def __init__(self):
        return SMSLive247Helper()

class SMSLive247Helper():
    
    def __init__(self):
        
        self.owneremail=''
        self.subacct = ''
        self.subacctpwd = ''
        self.sessid = 'aa1313a3-ac65-4aec-96a1-9e59a03ed134'
        #http://www.smslive247.com/http/index.aspx?cmd=login&owneremail=xxx&subacct=xxx&subacctpwd=xxx
    
    def sms_login(self):
        pass
    
    def send_sms(self, message_payload, **kwargs):
        try:
            payload = {'cmd': 'sendmsg',
                       'sessionid': self.sessid,
                       'message' : message_payload[1],
                       'sender' : message_payload[0],
                       'sendto' : message_payload[2][1:], #remove leading +
                       'msgtype' : 0             
                       }
            r = requests.post("http://www.smslive247.com/http/index.aspx", data=payload)
            if r.split(':')[0] is not 'OK':
                temp_log_to_db(
                    'sms',
                    [message_payload[0],message_payload[1],message_payload[2]],
                    message_err_code = (r.split(':')[1]).strip(),
                    owner = kwargs['owner']
                )
            else:
                messageid = (r.split(':')[1]).strip()
                #OK: 54142800
                #log message
                temp_log_to_db(
                    'sms',
                    sms_msg = [message_payload[0],message_payload[1],message_payload[2]],
                    message_id = messageid,
                    owner = kwargs['owner']
                )
            
                return(messageid)
            return r
        except:
            return(sys.exc_info())
    
    def get_sms_msg_status(self, messageid):
        
        try:
            payload = {'cmd': 'querymsgstatus',
                       'sessionid': self.sessid,
                       'messageid' : messageid  
                       }
            r = requests.get("http://www.smslive247.com/http/index.aspx", data=payload)
            return r
        except:
            pass
    


def ok_to_send(owner):
    #check user is active
    #check parent subscription not expired
    #check parent is active
    #check i have enough credit balance
    ## if company_wide_contacts, use admin balance for private and public
    ## for one-shot always use users balance
    cw = owner.parent.kitsystem.company_wide_contacts
    if cw is True: #company wide contacts set
        if owner.parent.user.is_active:
            if owner.parent.kitbilling.next_due_date >= timezone.now().date():
                if owner.parent.sms_balance >= 1: #parent has at least 1unit
                    return True
                else:
                    print("Not Enough Balance")
                    return False
            else:
                print("Parent Account Expired")
                return False
        else:
            print("Parent Account inactive")
            return False
                
    else:
        if owner.user.is_active:
            if owner.parent.kitbilling.next_due_date >= timezone.now().date():
                if owner.sms_balance >= 1:
                    return True
                else:
                    print("Not Enough Balance")
                    return False
            else:
                print("Parent Account Expired")
                return False
        else:
            print("User Account Inactive")
            return False
    
    
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