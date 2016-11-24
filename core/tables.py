'''
Created on May 23, 2016

@author: Dayo
'''

import json
import ast
import os

import django_tables2 as tables
from django_tables2.utils import A
from .models import Contact, MessageTemplate, Event, PublicEvent, ContactGroup, \
                    KITUser, SMTPSetting, CoUserGroup, FundsTransfer,\
                    UploadedContact, CustomData
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe


class TableSelectColumn(tables.CheckBoxColumn):
    
    def render(self):
        return self

class ContactTable(tables.Table):
    
    select = tables.CheckBoxColumn(accessor='pk')
    phone = tables.Column(verbose_name='Number')
    first_name = tables.LinkColumn(verbose_name="First Name", text=lambda t: t.first_name, args=[A('pk')])
    last_name = tables.Column(verbose_name="Last Name")
    active = tables.BooleanColumn(verbose_name="Active?")
    email = tables.EmailColumn(verbose_name="Email", text= lambda row: "%s..."%row.email[:10] if len(row.email) > 10 else row.email)
    nickname = tables.Column(verbose_name="Nickname")
    action = tables.Column(verbose_name="", accessor='pk', orderable=False)
    
    def render_phone(self,record):
        return mark_safe("<span>{}</span>".format(record.phone))
    
    def render_action(self, record):
        return mark_safe('<div style="width:6rem;"><a class="call-btn" href="#"><i style="font-size: 16pt;" class="fi-telephone"></i></a>'+\
                         '<a class="sms-btn" href="#"><i style="font-size: 16pt;" class="fi-mail"></i></a></div>'
                         )
    

    class Meta:
        model = Contact
        fields = ('select','first_name','last_name','nickname','email','phone','active','action')
        empty_text = "Sorry, No Contact Found"
        attrs = {'style': 'width: 100%'}
        
        
class ContactTable_Admin(tables.Table):
    
    select = tables.CheckBoxColumn(accessor='pk')
    phone = tables.Column(verbose_name='Number')
    first_name = tables.LinkColumn(verbose_name="First Name", text=lambda t: t.first_name, args=[A('pk')])
    last_name = tables.Column(verbose_name="Last Name")
    active = tables.BooleanColumn(verbose_name="Active?")
    kit_user = tables.Column(verbose_name="Created By")
    
    def render_phone(self,record):
        return mark_safe("<span>{}</span>".format(record.phone))

    class Meta:
        model = Contact
        fields = ('select','first_name','last_name','phone','active','kit_user')
        attrs = {'style': 'width: 100%'}
        empty_text = "Sorry, No Contact Found"
        
        
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
        attrs = {'style': 'width: 100%'}
        empty_text = "Sorry, No Private Anniversary Found"
        
class PublicEventTable(tables.Table):
    
    title = tables.LinkColumn(verbose_name="Title", args=[A('pk')])
    message = tables.Column(verbose_name="Message")
    date = tables.DateColumn(verbose_name="Date")
    kit_user = tables.Column(verbose_name="Created By")
    
    
    class Meta:
        model = PublicEvent
        fields = ('title','date', 'message', 'kit_user')
        attrs = {'style': 'width: 100%'}
        empty_text = "Sorry, No Public Anniversary Found"
    
class TemplateTable(tables.Table):
    
    title = tables.LinkColumn(verbose_name="Title", args=[A('pk')])
    smtp_setting = tables.Column(verbose_name="SMTP")
    send_sms = tables.BooleanColumn(verbose_name="SMS")
    cou_group = tables.Column(verbose_name="User Group")
    
    class Meta:
        model = MessageTemplate
        fields = ('title','smtp_setting', 'cou_group', 'send_sms')
        attrs = {'style': 'width: 100%'}
        empty_text = "Sorry, No Template Found"
        
        
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
        empty_text = "Sorry, No User Found"
        
class SMTPSettingsTable(tables.Table):
    
    description = tables.LinkColumn(verbose_name="Description", args=[A('pk')])
    smtp_server = tables.Column(verbose_name="SMTP Server")
    smtp_user = tables.Column(verbose_name="SMTP User")
    active = tables.BooleanColumn()
    
    
    class Meta:
        model = SMTPSetting
        fields = ('description', 'smtp_server', 'smtp_user','active')
        attrs = {'style': 'width: 100%'}
        empty_text = "Sorry, No SMTP Configuration Found"
        
        
class UserGroupsSettingsTable(tables.Table):
    
    title = tables.LinkColumn(verbose_name="Title", args=[A('pk')])
    description = tables.Column(verbose_name="Description")
    active = tables.BooleanColumn(verbose_name="Active")
    
    class Meta:
        model = CoUserGroup
        fields = ('title','description','active')
        attrs = {'style': 'width: 100%'}
        empty_text = "Sorry, No User Group Found"
        
        
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
        attrs = {'style': 'width: 100%'}
        empty_text = "Sorry, No Contact List Found"
        

class FundsTransferHistoryTable(tables.Table):
    
    from_user = tables.Column(verbose_name="From")
    to_user = tables.Column(verbose_name="To")
    amount = tables.Column(verbose_name="Amount")
    transaction_date = tables.Column(verbose_name="Transaction Time")
    
    
    def render_amount(self, record):
        return mark_safe('<span class="mamt-val">{0:.2f}</span>'.format(record.amount))
    
    class Meta:
        model = FundsTransfer
        fields = ('from_user','to_user','amount','transaction_date')
        attrs = {'style': 'width: 100%'}
        empty_text = "Sorry, No Transfer Found"
        
        
class UploadedContactFileHistoryTable(tables.Table):
    
    file_json = tables.Column(verbose_name="File")
    
    def render_file_json(self, record):
        if record.file_json:
            ext = record.file_extension
            if ext == 'csv':
                return mark_safe('<a href="{}"><i class="fi-page-csv" style="color: #10c710; font-size: 3rem;"></i></a>'.\
                                 format(record.get_absolute_url()))
            elif ext == 'xls':
                return mark_safe('<a href="{}"><i class="fi-page" style="color: #439243; font-size: 3rem;"></i></a>'.\
                                 format(record.get_absolute_url()))
            else:
                return mark_safe('<a href="{}"><i class="fi-page-filled" style="color: #ea1313; font-size: 3rem;"></i></a>'.\
                                 format(record.get_absolute_url()))
    
    class Meta:
        model = UploadedContact
        fields = ('name','file_json','import_status','upload_date')
        attrs = {'style': 'width: 100%'}
        empty_text = "Sorry, No Upload Found"


class CustomDataStoreTable(tables.Table):
    
    namespace = tables.LinkColumn(verbose_name="Namespace")
    system_id_field = tables.Column(verbose_name="Identity Field")
    identity_column_name = tables.Column(verbose_name="ID Key")
    created = tables.Column(verbose_name="Created")
        
    def render_namespace(self, record):        
        return format_html('<code><a href="{}" class="namespace_link">{}</a></code>',record.get_absolute_url(), record.namespace)
    
    class Meta:
        model = CustomData
        fields = ('namespace','system_id_field','identity_column_name','created')
        attrs = {'style': 'width: 100%'}
        empty_text = "Sorry, No CustomData Found"
        