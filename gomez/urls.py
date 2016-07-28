'''
Created on Jul 13, 2016

@author: Dayo
'''

from django.conf.urls import url, include

from .views import *
from .ajax import submit_issue_fb

urlpatterns = [
    url(r'^settings/', include([
                url(r'^system/(?P<pk>\d+)/$', SystemSettingsUpdateView.as_view(), name='system-settings'),
                url(r'^system/feedback/$', submit_issue_fb, name='system-user-feedback'),
                
    ])),
]