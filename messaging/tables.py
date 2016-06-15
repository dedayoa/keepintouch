'''
Created on Jun 10, 2016

@author: Dayo
'''

import django_tables2 as tables
from django_tables2.utils import A

from .models import StandardMessaging, AdvancedMessaging, ProcessedMessages
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from django.utils.translation import ugettext_lazy as _

import json
from django.forms.models import model_to_dict

class DraftStandardMessagesTable(tables.Table):
    
    __str__ = tables.Column(verbose_name="Message")
    recipients = tables.Column(verbose_name=_("Recipients"))
    last_modified = tables.DateTimeColumn(verbose_name="Last Edited")
    sms_sender = tables.Column(verbose_name="Sender")
    table_model_action = tables.LinkColumn(verbose_name="", \
                                           text=mark_safe('<span class="button small warning">Edit</span>'), \
                                           args=[A('pk')])


    
    def render_recipients(self, record):
        if record.recipients:
            if record.recipients.count() > 3:
                #return mark_safe('{} <span class="and-more">and more</span>'.format(", ".join(t.first_name for t in record.contacts.all()[0:2])))
            
                return mark_safe((format_html_join(', ', '<span>{} {}</span>',\
                                         ((t.first_name,t.last_name) for t in record.recipients.all()[0:3])
                                         ))+'<span class="and-more"> and more</span>')
            
            return format_html_join(', ', '<span>{} {}</span>',\
                                     ((t.first_name,t.last_name) for t in record.recipients.all())
                                    )
            
    class Meta:
        model = StandardMessaging
        fields = ('__str__','recipients','sms_sender','last_modified','table_model_action')
        
        
class DraftAdvancedMessagesTable(tables.Table):
    
    title = tables.Column(verbose_name="Title")
    message_template = tables.Column(verbose_name=_("Template"))
    contact_group = tables.Column(verbose_name="Recipient")
    last_modified = tables.DateTimeColumn(verbose_name="Last Edited")
    table_model_action = tables.LinkColumn(verbose_name="", \
                                           text=mark_safe('<span class="button small warning">Edit</span>'), \
                                           args=[A('pk')])


    
    def render_contact_group(self, record):
        if record.contact_group:
            if record.contact_group.count() > 2:

                return mark_safe(", ".join(t.title for t in record.contact_group.all()[0:2])+\
                                 '<span class="and-more"> and more</span>')
            
            return ", ".join(t.title for t in record.contact_group.all())
            
    class Meta:
        model = AdvancedMessaging
        fields = ('title','message_template','contact_group','last_modified','table_model_action')
        
        
class ProcessedMessagesTable(tables.Table):
    
    message = tables.Column(verbose_name="Message")
    message_type = tables.Column("Type")
    created = tables.DateTimeColumn(verbose_name="Processed at")
    
    def render_message(self, record):
        
        serialized_m = json.dumps(record.message)
        
        return mark_safe('<a href="#" data-kitmsg=\'{}\' class="show-message-modal">{}</a>'.\
            format(serialized_m, "Hi"))
    
    class Meta:
        model = ProcessedMessages
        fields = ['message','message_type','created']
    