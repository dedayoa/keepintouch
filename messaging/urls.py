'''
Created on Jun 10, 2016

@author: Dayo
'''


from django.conf.urls import url, include


from .views import *

urlpatterns = [
    url(r'^create/success/$', StandardMessageCreateView.as_view(), name=''),
    
    url(r'^standard/', include([
                url(r'^new/$', StandardMessageCreateView.as_view(), name='new-standard-message'),
                url(r'^draft/(?P<pk>\d+)/$', StandardMessageUpdateDraftView.as_view(), name='standard-message-draft'),
                url(r'^(draft|waiting|processed)/$', StandardMessageCreateView.as_view(), name='message-list-by-status'),
                ])),
    url(r'^advanced/new/$', AdvancedMessageCreateView.as_view(), name='new-advanced-message'),
    
]