'''
Created on Sep 19, 2016

@author: Dayo
'''

import requests
from django.conf import settings
from requests import exceptions

from .exceptions import GoogleAPIError


class GoogleURLShortener:
    
    def __init__(self):
        self.base_url = "https://www.googleapis.com/urlshortener/v1/url?key="+settings.GOOGAPI_KEY
        
    def make_request(self, method, urlpath, payload=None, headers=None):        
        try:            
            s = requests.Session()
            s.headers.update({'Content-Type': 'application/json','accept': "application/json"})
            
            if method == 'post':
                response = s.post(
                        '{}{}'.format(self.base_url,urlpath),
                        headers = headers,
                        json = payload
                                  )
            elif method == 'get':
                response = s.get(
                        '{}{}'.format(self.base_url,urlpath),
                        headers = headers,
                        json = payload
                                  )
                
            if response.json().get('error'):
                raise GoogleAPIError(response.json()['error'])
            else:
                return response
        
        except exceptions.ConnectionError:
            print("Connection Error")

    def get_short_url(self, longurl):
        payload = {'longUrl': longurl}
        res = self.make_request('post','', payload)
        return res.json()['id']
    
    def get_short_url_analytics(self, shorturl):
        urlpath = '&shortUrl='+shorturl+'&projection=FULL'
        res = self.make_request('get', urlpath)
        return res.json()  