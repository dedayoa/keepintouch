'''
Created on May 22, 2016

@author: Dayo
'''


from django.conf.urls import url, include


from .views import *
from .ajax import get_system_stats, get_qpc_stats, sms_credit_transfer, get_user_sms_balance,\
                    get_contact_file_upload, now_import_contacts


urlpatterns = [
    #url(r'^$', Index.as_view(), name='index'),
    url(r'^exit/$', exitdoor , name='backdoor'),
    url(r'^$', entrance, name='frontdoor'),
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard-view'),
    url(r'^ping-stat/', include([
                url(r'^system/$', get_system_stats, name='system-stat'),
                url(r'^qpc/$', get_qpc_stats, name='qpc-stat'),
    ])),
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
                
                #Accounts
                url(r'^account/$', AccountManagementView.as_view(), name='account-mgmt'),
                url(r'^account/sms/$', SMSBalanceTransferView.as_view(), name='sms-account-mgmt'),
                url(r'^account/sms/credit_transfer/$', sms_credit_transfer, name='sms-credit-transfer'),
                url(r'^account/sms/get_user_balance/$', get_user_sms_balance),
                
                #my profile
                url(r'^user/me/$', KITUserPersonalProfileView.as_view(), name='kituser-personal-profile'),
    ])),
    #Data Management
    url(r'^data-mgmt/', include([
                url(r'import_contact/$', ContactImportView.as_view(), name='contact-import'),
                url(r'import_contact/upload/$', get_contact_file_upload, name='contact-upload-action'),
                url(r'import_contact/import/$', now_import_contacts, name='contact-import-action'),
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