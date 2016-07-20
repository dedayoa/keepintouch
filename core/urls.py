'''
Created on May 22, 2016

@author: Dayo
'''


from django.conf.urls import url, include


from .views import *


urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^settings/', include([
                url(r'^users/$', kituser_settings, name='kituser-settings-list'),
                url(r'^user/(?P<pk>\d+)/$', KITUserUpdateView.as_view(), name='kituser-detail'),
                url(r'^user/new/$', UserCreateView.as_view(), name='kituser-new'),
                
                #User Groups
                url(r'^user-groups/$', usergroup_settings, name='usergroup-list'),
                url(r'^user-groups/(?P<pk>\d+)/$', UserGroupUpdateView.as_view(), name='usergroup-detail'),
                #SMTP
                url(r'^smtps/$', smtp_settings, name='smtp-settings-list'),
                url(r'^smtp/(?P<pk>\d+)/$', SMTPUpdateView.as_view(), name='smtp-detail'),
                url(r'^smtp/new/$', SMTPCreateView.as_view(), name='smtp-new'),
                url(r'^smtp/(?P<pk>\d+)/delete/$', SMTPDeleteView.as_view(), name='smtp-delete'),
                url(r'^smtp/(?P<pk>\d+)/check/$', CheckSMTPServerView.as_view(), name='smtp-check'),
    ])),

    #User Groups
    url(r'^contact-groups/$', contactgroups, name='contactgroup-list'),
    url(r'^contact-group/', include([
                url(r'^new/$', ContactGroupCreateView.as_view(), name='contactgroup-new'),
                url(r'^(?P<pk>\d+)/$', ContactGroupUpdateView.as_view(), name='contactgroup-detail'),
                url(r'^(?P<pk>\d+)/delete/$', ContactGroupDeleteView.as_view(), name='contactgroup-delete'),
    ])),
    url(r'^contacts/$', contacts, name='contacts-list'), #lists all contacts
    url(r'^contact/', include([
                url(r'^(?P<pk>[A-Z0-9]{9})/$', ContactViewView.as_view(), name='contact-detail'),
                url(r'^(?P<pk>[A-Z0-9]{9})/delete/$', ContactDeleteView.as_view(), name='contact-delete'),
                url(r'^new/$', ContactCreateView.as_view(), name='contact-new')
    ])),
    url(r'^events/$', privateevents, name='events-list'), #lists all contacts
    url(r'^events/public/$', publicevents, name='public-events-list'), #lists all contacts
    url(r'^event/public/', include([
                url(r'^(?P<pk>\d+)/$', PublicEventUpdateView.as_view(), name='public-event-detail'),
                url(r'^(?P<pk>\d+)/delete/$', PublicEventDeleteView.as_view(), name='public-event-delete'),
                url(r'^new/$', PublicEventCreateView.as_view(), name='public-event-new')
    ])),
    url(r'^templates/$', templates, name='templates-list'),
    url(r'^template/', include([
                url(r'^(?P<pk>\d+)/$', MessageTemplateUpdateView.as_view(), name='templates-detail'),
                url(r'^new/$', MessageTemplateCreateView.as_view(), name='template-new'),
                url(r'^(?P<pk>\d+)/delete/$', MessageTemplateDeleteView.as_view(), name='template-delete')
    ])),
]