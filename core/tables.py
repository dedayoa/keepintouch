'''
Created on May 23, 2016

@author: Dayo
'''

import django_tables2 as tables
from django_tables2.utils import A
from .models import Contact, MessageTemplate, Event, PublicEvent,\
                    KITUser, KITAdminAccount, SMTPSetting
from django.utils.html import format_html


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
    
    
    class Meta:
        model = PublicEvent
        fields = ('title','date', 'message', 'group')
    