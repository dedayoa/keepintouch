
import requests
from requests import exceptions
from django.conf import settings
from django.core.urlresolvers import reverse
import base64
import ast, json

from reportng.models import SMSDeliveryReport, SMSDeliveryReportHistory
from core.exceptions import SMSGatewayError


class Configuration:
    
    def __init__(self, username = None, password = None, api_key = None, token = None, base_url = None):
        
        self.base_url = "https://api.infobip.com"
        self.delivery_report_callback = reverse('infobip-delivery-url')
        
        if base_url:
            self.base_url = base_url
        
        self.username = username
        self.password = password
        self.api_key = api_key
        self.token = token
        
    def get_auth_basic_key(self):
        c = '%s:%s'%(self.username, self.password)
        return base64.urlsafe_b64encode(bytes(c,'utf-8'))
        
class InfobipSMS():
    
    def __init__(self):
        self.base_url = "https://api.infobip.com"
        self.username = settings.INFOBIP_USERNAME
        self.password = settings.INFOBIP_PASSWORD
        
        
    def make_request(self, urlpath, payload=None, headers=None):
        
        try:
            
            s = requests.Session()
            s.auth = (self.username, self.password)
            s.headers.update({'Content-Type': 'application/json','accept': "application/json"})
            
            request = s.post(
                    '{}{}'.format(self.base_url,urlpath),
                    headers = headers,
                    json = payload
                              )
            return request
        except exceptions.ConnectionError:
            print("Connection Error")
            
    
    def send_single_sms(self):
        
        message = {
            "from":"MrDahzle",
            "to" : "+2348028443225",
            'text' : "This is an Infobip Deliverd Text"
                   }
        
        r = self.make_request('/sms/1/text/single/', payload=message)
        print(r.json())
        print(r.text)
        print(r.headers)
        
    
    def send_single_advanced_sms(self, message, kuser, batchid=None):
        
        sms_from = message[0]
        to_phone = message[2]
        sms_message = message[1]
        
        res = SMSDeliveryReport.objects.create(
                        origin = '0',
                        sms_sender = sms_from,
                        to_phone = to_phone,
                        sms_message = {'text' : sms_message},
                        sms_gateway = {},
                        kituser_id = kuser.id,
                        kitu_parent_id = kuser.get_parent().id
                        )
        
        message = {
            "bulkId": str(batchid),
            "messages":[
                {
                   "from": sms_from,
                   "destinations":[
                      {
                         "to": to_phone,
                         "messageId": str(res.id),
                      },
                   ],
                   "text": sms_message,
                   "intermediateReport": True,
                   "notifyUrl": settings.WEBHOOK_BASE_URL+reverse('reports:infobip-delivery-url'),
                   "validityPeriod": 720,
                   "callbackData": "{}".format(settings.WEBHOOK_KEY)
                }]
            }
        
        r = self.make_request('/sms/1/text/advanced', payload=message)
        r_v = r.json()
        
        if r_v.get('requestError'):          
            raise SMSGatewayError(r_v.get('requestError'))
        else:
        
            #print(type(v))
            SMSDeliveryReportHistory.objects.create(message_id = res, data=r_v)
            
            res.msg_status = r_v['messages'][0]['status']['groupId']
            res.save()