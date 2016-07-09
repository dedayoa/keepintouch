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
            
    def test_smtp_server(self):
        
        try:
            
            conn = self._get_connection()                 
            
            with conn as smtp_connection:
                mail.EmailMessage(
                    'Test Email from IntouchNG',
                    'This is a test email to check your SMTP setup',
                    self.smtp_user,
                    ['server-test@intouch.com.ng'],
                    connection=smtp_connection,
                ).send()
                                
            return True
        except Exception:
            return(sys.exc_info())

    
    def send_email(self, email_message):
        
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
    
#todo :    
class SMSHelper():
    
    def __init__(self):
        
        self.owneremail=''
        self.subacct = ''
        self.subacctpwd = ''
        self.sessid = 'aa1313a3-ac65-4aec-96a1-9e59a03ed134'
        #http://www.smslive247.com/http/index.aspx?cmd=login&owneremail=xxx&subacct=xxx&subacctpwd=xxx
    
    def sms_login(self):
        pass
    
    def send_sms(self, message_payload):
        try:
            payload = {'cmd': 'sendmsg',
                       'sessionid': urlencode(self.sessid),
                       'message' : urlencode(message_payload[1]),
                       'sender' : urlencode(message_payload[0]),
                       'sendto' : urlencode(message_payload[2]),
                       'msgtype' : 0                   
                       }
            r = requests.post("http://www.smslive247.com/http/index.aspx", data=payload)
            messageid = (r.split(':')[1]).strip()
            #OK: 54142800
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
    
