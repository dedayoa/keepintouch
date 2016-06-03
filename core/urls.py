'''
Created on May 22, 2016

@author: Dayo
'''


from django.conf.urls import url, include


from .views import *

urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^settings/$', settings, name='settings'),
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