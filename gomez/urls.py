'''
Created on Jul 13, 2016

@author: Dayo
'''

from django.conf.urls import url, include

from .views import *

urlpatterns = [
    url(r'^settings/', include([
                url(r'^system/(?P<pk>\d+)/$', SystemSettingsUpdateView.as_view(), name='system-settings'),
                
                
    ])),
]