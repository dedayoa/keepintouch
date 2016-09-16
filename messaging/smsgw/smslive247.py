'''
Created on Sep 16, 2016

@author: Dayo
'''

import requests
from core.exceptions import SMSGatewayError

class SMSLive247Helper():
    
    def __init__(self):
        
        self.owneremail=''
        self.subacct = ''
        self.subacctpwd = ''
        self.sessid = 'aa1313a3-ac65-4aec-96a1-9e59a03ed134'
        #http://www.smslive247.com/http/index.aspx?cmd=login&owneremail=xxx&subacct=xxx&subacctpwd=xxx
    
    def sms_login(self):
        pass
    
    def send_sms(self, message_payload):
        payload = {'cmd': 'sendmsg',
                   'sessionid': self.sessid,
                   'message' : message_payload[1],
                   'sender' : message_payload[0],
                   'sendto' : message_payload[2][1:], #remove leading +
                   'msgtype' : 0
                   }
        r = requests.post("http://www.smslive247.com/http/index.aspx", data=payload)
        
        if (r.text).split(':')[0] == 'OK':
        # was using is and it caused all sorts of problems. Identity is not equality
        # http://stackoverflow.com/questions/1504717/why-does-comparing-strings-in-python-using-either-or-is-sometimes-produce
            return r.text
        else:                    
            # raise ALERT!!! log this for admin
            raise SMSGatewayError(r.text) #e.g ERR: 404: Insufficient credit to complete request
        
    
    def get_sms_msg_status(self, messageid):
        
        try:
            payload = {'cmd': 'querymsgstatus',
                       'sessionid': self.sessid,
                       'messageid' : messageid  
                       }
            r = requests.get("http://www.smslive247.com/http/index.aspx", data=payload)
            return r.text
        except:
            pass



    