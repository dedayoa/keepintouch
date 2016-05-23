'''
Created on May 22, 2016

@author: Dayo
'''


from django.conf.urls import url, include


from .views import *

urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^settings/$', settings, name='settings'),
    url(r'^contacts/$', contacts, name='contact'), #lists all contacts
    url(r'^contact/', include([
                url(r'^(?P<cusid>[A-Z0-9]{9})/$', Contact.as_view(), name='contact'),
                url(r'^new/$', NewContact.as_view(), name='contact')
    ]))
]