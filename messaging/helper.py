'''
Created on Jul 9, 2016

@author: Dayo
'''
import sys
import requests

from django.utils.http import urlencode

from django.core import mail
from django.core.mail import send_mail, EmailMessage
from django.core.mail.backends.smtp import EmailBackend

from django.core.validators import validate_email
from .models import SMSReport, EmailReport





def temp_log_to_db(m_type, **kwargs):
    
    if m_type == 'email':
        EmailReport.objects.create(
            to_email = kwargs['email_msg'][3],
            from_email = kwargs['email_msg'][2],
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
                    ['dayo@windom.biz','server-test@intouch.com.ng'],
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
                    from_email = self.from_sender,
                    to = email_message[2], #recipient
                    connection=smtp_connection,
                    #headers={'Message-ID': 'foo'},
                )
                msg.content_subtype = "html"
                msg.send()
                
                temp_log_to_db(
                    'email',
                    [email_message[0],email_message[1],email_message[2], email_message[3]],
                    owner = kwargs['owner']
                )
        except Exception:
            temp_log_to_db(
                'email',
                [email_message[0],email_message[1],email_message[2], email_message[3]],
                gw_err_preamble = str(sys.exc_info()),
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
                       'sessionid': urlencode(self.sessid),
                       'message' : urlencode(message_payload[1]),
                       'sender' : urlencode(message_payload[0]),
                       'sendto' : urlencode((message_payload[2])[1:]), #remove leading +
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
        except Exception:
            print('Exception')
    
    def get_sms_msg_status(self, messageid):
        
        try:
            payload = {'cmd': 'querymsgstatus',
                       'sessionid': urlencode(self.sessid),
                       'messageid' : urlencode(messageid)    
                       }
            r = requests.get("http://www.smslive247.com/http/index.aspx", data=payload)
            return r
        except:
            pass
    