'''
Created on Jun 10, 2016

@author: Dayo
'''


from django.conf.urls import url, include


from .views import *
from .ajax import prepare_to_send_message, send_message, run_reminder, submit_issue_fb

urlpatterns = [
    url(r'^create/success/$', StandardMessageCreateView.as_view(), name=''),
    url(r'^prepare-to-send-message/$', prepare_to_send_message, name='messages-prepare-send-message'),
    url(r'^send-message/$', send_message, name='messages-send-message'),
    url(r'^run-reminder/$', run_reminder, name='run-reminder-message'),
    url(r'^processed/messages/$', message_processed_status_view, name='messages-processed-status'),
    url(r'^queued/messages/$', message_queued_status_view, name='messages-queued-status'),
    url(r'^queued/message/(?P<mtype>ADVANCED|STANDARD)/(?P<pk>\d+)/dequeue/$', queued_message_dequeue_view, name='queued-message-dequeue'),
    
    url(r'^running/messages/$',  message_running_status_view, name='messages-running-status'),
    url(r'^running/message/REMINDER/(?P<pk>\d+)/dequeue/$', queued_message_dequeue_view, name='running-message-dequeue'),
    
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
    url(r'^system/feedback/$', submit_issue_fb, name='system-user-feedback'),
    url(r'^failed/', include([
            url(r'^messages/$', failed_kit_messages_view, name='kit-messages-failed'),
            url(r'^message/(?P<pk>\d+)/retry/$', failed_messaging_retry, name='failed-kit-message-retry'),
            url(r'^smss/$', failed_sms_messages_view, name='sms-messages-failed'),
            url(r'^sms/(?P<pk>\d+)/retry/$', failed_sms_message_retry, name='failed-sms-message-retry'),
            url(r'^emails/$', failed_email_messages_view, name='email-messages-failed'),
            url(r'^email/(?P<pk>\d+)/retry/$', failed_email_message_retry, name='failed-email-message-retry'),
            ])),
    
]