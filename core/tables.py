'''
Created on May 23, 2016

@author: Dayo
'''

import django_tables2 as tables
from django_tables2.utils import A
from .models import Contact, MessageTemplate, Event, PublicEvent, ContactGroup, \
                    KITUser, KITAdminAccount, SMTPSetting, CoUserGroup, SMSTransfer
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe


class TableSelectColumn(tables.CheckBoxColumn):
    
    def render(self):
        return self

class ContactTable(tables.Table):
    
    select = tables.CheckBoxColumn(accessor='pk')
    first_name = tables.LinkColumn(verbose_name="First Name", text=lambda t: t.first_name, args=[A('pk')])
    last_name = tables.Column(verbose_name="Last Name")
    active = tables.BooleanColumn(verbose_name="Active?")
    kit_user = tables.Column(verbose_name="Created By")

    class Meta:
        model = Contact
        fields = ('select','first_name','last_name','kit_user','active')
        
        
class PrivateEventTable(tables.Table):
    
    message = tables.Column(verbose_name="Template")
    title = tables.Column(verbose_name="Title")
    date = tables.DateColumn(verbose_name="Date")
    contact = tables.LinkColumn( verbose_name="Contact")
    
    def render_contact(self, record):
        #if record.contacts.exists():
            #return(str(p.pk for p in record.contacts.all()))
        if record.contact:
            return format_html('<a href="{}">{}</a>',record.contact.get_absolute_url(),\
                                "{} {}".format(record.contact.first_name,record.contact.last_name))
            #or use >> reverse('core:contact-detail',kwargs={'pk':record.contact.pk})
     
    class Meta:
        model = Event
        fields = ('contact','date','title','message')
        
class PublicEventTable(tables.Table):
    
    title = tables.LinkColumn(verbose_name="Title", args=[A('pk')])
    message = tables.Column(verbose_name="Message")
    date = tables.DateColumn(verbose_name="Date")
    kit_user = tables.Column(verbose_name="Created By")
    
    
    class Meta:
        model = PublicEvent
        fields = ('title','date', 'message', 'kit_user')
    
class TemplateTable(tables.Table):
    
    title = tables.LinkColumn(verbose_name="Title", args=[A('pk')])
    smtp_setting = tables.Column(verbose_name="SMTP")
    send_sms = tables.BooleanColumn(verbose_name="SMS")
    cou_group = tables.Column(verbose_name="User Group")
    
    class Meta:
        model = MessageTemplate
        fields = ('title','smtp_setting', 'cou_group', 'send_sms')
        
        
class KITUsersTable(tables.Table):
    
    '''
    user = tables.LinkColumn(verbose_name="User")
    groups = tables.Column(verbose_name="Groups", accessor='pk')
    company = tables.Column()
    phone_number = tables.Column()
    last_login = tables.DateTimeColumn(verbose_name="Last Login")
    
    def __init__(self, *args, **kwargs):
        super(KITUsersTable, self).__init__(*args, **kwargs)
        
    def render_last_login(self, record):
        if record.user:
            return record.user.last_login
    
    def render_user(self, record):
        if record.user:
            return format_html(
                    '<a href="{}">{}</a>', record.get_absolute_url(),\
                    "{} {}".format(record.user.first_name, record.user.last_name)   
                    )
    
    def render_groups(self, record):
        if record.user:
            #return format_html('{}',record.user.first_name)
            return (", ".join(t.title for t in record.groups_belongto.all()))
    '''
    
    class Meta:
        model = KITUser
        #fields = ('user', 'company', 'phone_number', 'groups')
        
class SMTPSettingsTable(tables.Table):
    
    description = tables.LinkColumn(verbose_name="Description", args=[A('pk')])
    smtp_server = tables.Column(verbose_name="SMTP Server")
    smtp_user = tables.Column(verbose_name="SMTP User")
    active = tables.BooleanColumn()
    
    
    class Meta:
        model = SMTPSetting
        fields = ('description', 'smtp_server', 'smtp_user','active')
        
        
class UserGroupsSettingsTable(tables.Table):
    
    title = tables.LinkColumn(verbose_name="Title", args=[A('pk')])
    description = tables.Column(verbose_name="Description")
    active = tables.BooleanColumn(verbose_name="Active")
    
    class Meta:
        model = CoUserGroup
        fields = ('title','description','active')
        
        
class ContactGroupsSettingsTable(tables.Table):
    
    title = tables.LinkColumn(verbose_name="Title", args=[A('pk')])
    description = tables.Column(verbose_name="Description")
    last_modified = tables.DateTimeColumn(verbose_name="Modified")
    contacts = tables.Column(verbose_name="Contacts")
    
    def render_contacts(self, record):
        if record.contacts:
            if record.contacts.count() > 3:
                #return mark_safe('{} <span class="and-more">and more</span>'.format(", ".join(t.first_name for t in record.contacts.all()[0:2])))
            
                return mark_safe((format_html_join(', ', '<span>{} {}</span>',\
                                         ((t.first_name,t.last_name) for t in record.contacts.all()[0:3])
                                         ))+'<span class="and-more"> and more</span>')
            
            return format_html_join(', ', '<span>{} {}</span>',\
                                     ((t.first_name,t.last_name) for t in record.contacts.all())
                                    )
            #return record.contacts.count()
            
    
    class Meta:
        model = ContactGroup
        fields = ('title','description','contacts','last_modified')
        

class SMSTransferHistoryTable(tables.Table):
    
    from_user = tables.Column(verbose_name="From")
    to_user = tables.Column(verbose_name="To")
    sms_units = tables.Column(verbose_name="SMS Units")
    transaction_date = tables.Column(verbose_name="Transaction Time")
    
    class Meta:
        model = SMSTransfer
        fields = ('from_user','to_user','sms_units','transaction_date')
        