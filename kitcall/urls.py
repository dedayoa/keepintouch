'''
Created on Nov 8, 2016

@author: Dayo
'''

from django.conf.urls import url, include

from .views import *
from .ajax import call_number

urlpatterns = [
    url(r'^dial/(?P<pn>\d+)/$', call_number, name='ajax-dial-number'),
                ]