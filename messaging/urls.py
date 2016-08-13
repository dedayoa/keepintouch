'''
Created on Jun 10, 2016

@author: Dayo
'''


from django.conf.urls import url, include


from .views import *
from .ajax import prepare_to_send_message, send_message

urlpatterns = [
    url(r'^create/success/$', StandardMessageCreateView.as_view(), name=''),
    url(r'^prepare-to-send-message/$', prepare_to_send_message, name='messages-prepare-send-message'),
    url(r'^send-message/$', send_message, name='messages-send-message'),
    url(r'^processed/messages/$', message_processed_status_view, name='messages-processed-status'),
    url(r'^queued/messages/$', message_queued_status_view, name='messages-queued-status'),
    url(r'^queued/message/(?P<mtype>ADVANCED|STANDARD)/(?P<pk>\d+)/dequeue/$', queued_message_dequeue_view, name='queued-message-dequeue'),
    url(r'^standard/', include([
                url(r'^new/$', StandardMessageCreateView.as_view(), name='new-standard-message'),
                url(r'^draft/(?P<pk>\d+)/$', StandardMessageUpdateDraftView.as_view(), name='standard-message-draft'),
                url(r'^draft/messages/$', standard_message_draft_view, name='standard-draft-messages'),
                url(r'^message/(?P<pk>\d+)/delete/$', StandardMessageDeleteView.as_view(), name='standard-message-delete'),
                ])),
    url(r'^advanced/', include([
                url(r'^new/$', AdvancedMessageCreateView.as_view(), name='new-advanced-message'),
                url(r'^draft/(?P<pk>\d+)/$', AdvancedMessageUpdateDraftView.as_view(), name='advanced-message-draft'),
                url(r'^draft/messages/$', advanced_message_draft_view, name='advanced-draft-messages'),
                url(r'^message/(?P<pk>\d+)/delete/$', AdvancedMessageDeleteView.as_view(), name='advanced-message-delete'),
                
                ])),
    url(r'^reminder/', include([
            url(r'^new/$', ReminderCreateView.as_view(), name='new-reminder-message'),
            url(r'^draft/(?P<pk>\d+)/$', ReminderUpdateDraftView.as_view(), name='reminder-message-draft'),
            url(r'^draft/messages/$', reminder_draft_view, name='reminder-draft-messages'),
            url(r'^message/(?P<pk>\d+)/delete/$', ReminderDeleteView.as_view(), name='reminder-message-delete'),
            ])),
    
]