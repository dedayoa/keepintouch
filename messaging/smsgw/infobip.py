
import requests
from requests import exceptions
from django.conf import settings
import base64


class Configuration:
    
    def __init__(self, username = None, password = None, api_key = None, token = None, base_url = None):
        
        self.base_url = "https://api.infobip.com"
        
        if base_url:
            self.base_url = base_url
        
        self.username = username
        self.password = password
        self.api_key = api_key
        self.token = token
        
    def get_auth_basic_key(self):
        c = '%s:%s'%(self.username, self.password)
        return base64.urlsafe_b64encode(bytes(c,'utf-8'))
        
class InfobipSMS:
    
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
        
    def single_advanced_sms(self):
        
        message = {
            "from":"MrDee",
            "to" : "+2348028443225",
            'text' : "This is an Infobip Deliverd Text"
                   }
        
        r = self.make_request('/sms/1/text/advanced', payload=message)