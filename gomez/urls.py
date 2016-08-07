'''
Created on Jul 13, 2016

@author: Dayo
'''

from django.conf.urls import url, include

from .views import *
from .ajax import submit_issue_fb, upload_custom_data, process_1_custom_data,\
                get_custom_data_ajax, delete_custom_data_ajax

urlpatterns = [
    url(r'^settings/', include([
                url(r'^system/(?P<pk>\d+)/$', SystemSettingsUpdateView.as_view(), name='system-settings'),
                url(r'^system/feedback/$', submit_issue_fb, name='system-user-feedback'),
                
    ])),
    url(r'^data-mgmt/', include([
                url(r'^custom-data/upload/$', upload_custom_data, name='upload-custom-data'),
                url(r'^custom-data/process-a/$', process_1_custom_data),
                url(r'^custom-data/(?P<pk>\w{5})/$', get_custom_data_ajax, name='custom-data-ajax'),
                url(r'^custom-data/(?P<pk>\w{5})/delete/$', delete_custom_data_ajax, name='delete-custom-data-ajax'),
                
    ])),
]