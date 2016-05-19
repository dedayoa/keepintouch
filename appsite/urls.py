'''
Created on May 19, 2016

@author: Dayo
'''
from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^settings/$', settings, name='settings'),
    url(r'^contact/$', contact, name='contact'),
]
