'''
Created on May 22, 2016

@author: Dayo
'''


from django.conf.urls import url, include


from .views import *

urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^settings/$', settings, name='settings'),
    url(r'^contacts/$', contacts, name='all_contact'), #lists all contacts
    url(r'^contact/', include([
                url(r'^(?P<contactid>[A-Z0-9]{9})/$', ContactView.as_view(), name='contact_detail'),
                url(r'^new/$', NewContactView.as_view(), name='new_contact')
    ]))
]