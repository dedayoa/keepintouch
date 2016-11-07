'''
Created on Sep 13, 2016

@author: Dayo
'''


from django.conf.urls import url, include


from .views import *
from .webhooks import *

urlpatterns = [
    #url(r'^$', Index.as_view(), name='index'),
    url(r'^sms/$', SMSReport.as_view(), name='sms-reports'),
    url(r'^email/$', EmailReport.as_view(), name='email-reports'),
    url(r'^sms/delivery/infobip/$', infobip_sms_delivery_report_callback, name='infobip-delivery-url'),
    url(r'^webhook/cdr/$', fs_call_detail_report_callback, name='fs-cdr-url'),
]