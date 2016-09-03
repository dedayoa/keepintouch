'''
Created on May 22, 2016

@author: Dayo
'''


from django.conf.urls import url, include


from .views import *
from .ajax import *
from .helper import UploadedContactsDownloadView

urlpatterns = [
    #url(r'^$', Index.as_view(), name='index'),
    url(r'^exit/$', exitdoor , name='backdoor'),
    url(r'^$', entrance, name='frontdoor'),
    url(r'^register/free-trial/$', register_free_trial, name='freetrial-signup'),
    url(r'^gcrawler/$', crawler_entrance, name="gcrawler"),
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
                url(r'^user-group/(?P<pk>\d+)/$', UserGroupUpdateView.as_view(), name='usergroup-detail'),
                url(r'^user-group/(?P<pk>\d+)/delete/$', UserGroupDeleteView.as_view(), name='usergroup-delete'),
                url(r'^user-group/new/$', UserGroupCreateView.as_view(), name='usergroup-new'),
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
                
                url(r'^account/user/send-verify-code/$', send_verification_code, name='send-verification-code'),
                url(r'^account/user/verify/$', verify_user_details, name='now-validate-user-details'),
                
                #my profile
                url(r'^user/me/$', KITUserPersonalProfileView.as_view(), name='kituser-personal-profile'),
    ])),
    #Data Management
    url(r'^data-mgmt/', include([
                url(r'import_contact/$', ContactImportView.as_view(), name='contact-import'),
                url(r'import_contact/upload/$', get_contact_file_upload, name='contact-upload-action'),
                url(r'import_contact/import/$', now_import_contacts, name='contact-import-action'),
                url(r'custom_data/$', CustomDataView.as_view(), name='custom-data'),
                url(r'export/$', now_import_contacts, name='export-data'),
                url('^contact/(?P<id>[A-Za-z0-9_-]+)/download/$',UploadedContactsDownloadView.as_view(), name='download-contact-file'),
    ])),
    #custom Data
    url(r'^data-mgmt/', include([
                url(r'^custom-data/upload/$', upload_custom_data, name='upload-custom-data'),
                url(r'^custom-data/process-a/$', process_1_custom_data),
                url(r'^custom-data/(?P<pk>\w{6})/$', get_custom_data_ajax, name='custom-data-ajax'),
                url(r'^custom-data/(?P<pk>\w{6})/delete/$', delete_custom_data_ajax, name='delete-custom-data-ajax'),
                url(r'^custom-data/headers/(?P<pk>\w{6})/$', get_custom_data_columns, name='custom-data-columns'),
                url(r'^custom-data/headers/$', get_custom_data_columns),
    ])),


    #User Groups
    url(r'^contact-lists/$', contactgroups, name='contactgroup-list'),
    url(r'^contact-list/', include([
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