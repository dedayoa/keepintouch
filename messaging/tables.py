'''
Created on Jun 10, 2016

@author: Dayo
'''

import django_tables2 as tables
from django_tables2.utils import A

from .models import StandardMessaging, AdvancedMessaging, ProcessedMessages, QueuedMessages,\
                    ReminderMessaging
from django.utils.html import format_html_join, format_html
from django.utils.safestring import mark_safe

from django.utils.translation import ugettext_lazy as _

import json
import re
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse

class DraftStandardMessagesTable(tables.Table):
    
    title = tables.Column(verbose_name="Title")
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
    
    def render_title(self, record):
        if record.title:
            text_2_wordlist = re.sub("[^\w]", " ",  record.title).split()
            return format_html('<span data-tooltip aria-haspopup="true" class="has-tip" data-disable-hover="false" tabindex=1 title="{}">{}</span>',\
                               record.__str__(),
                               #nltk.sent_tokenize(record.title)[0:5].join(" ")
                               (" ".join(text_2_wordlist[0:3])+"...") if len(text_2_wordlist) > 3 else record.title 
                               )
            
    class Meta:
        model = StandardMessaging
        fields = ('title','recipients','sms_sender','last_modified','table_model_action')
        
        
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
    processed_at = tables.DateTimeColumn(verbose_name="Processed at")
    
    def render_message(self, record):
        
        serialized_m = json.dumps(record.message)
        
        return mark_safe('<a href="#" data-kitmsg=\'{}\' class="show-message-modal">{}</a>'.\
            format(serialized_m, (record.message)['title']))
    
    class Meta:
        model = ProcessedMessages
        fields = ['message','message_type','processed_at']
        
        
class QueuedMessagesTable(tables.Table):
    
    class Meta:
        model = QueuedMessages
        fields = ['message','message_type','delivery_time','message_id']
    
    
class DraftReminderMessagesTable(tables.Table):
    
    table_model_action = tables.LinkColumn(verbose_name="", \
                                       text=mark_safe('<span class="button small warning">Edit</span>'), \
                                       args=[A('pk')])
    title = tables.Column(verbose_name="Title")
    custom_data_namespace = tables.Column(verbose_name="Namespace")
    last_modified = tables.DateTimeColumn(verbose_name="Last Edited")
    contact_group = tables.Column(verbose_name="Contact Group")
    
    def render_title(self, record):
        if record.title:
            text_2_wordlist = re.sub("[^\w]", " ",  record.title).split()
            return format_html('<span data-tooltip aria-haspopup="true" class="has-tip" data-disable-hover="false" tabindex=1 title="{}">{}</span>',\
                               record.__str__(),
                               (" ".join(text_2_wordlist[0:3])+"...") if len(text_2_wordlist) > 3 else record.title 
                               )
    
    def render_contact_group(self, record):
        if record.contact_group:
            if record.contact_group.count() > 2:

                return mark_safe(", ".join(t.title for t in record.contact_group.all()[0:2])+\
                                 '<span class="and-more"> and more</span>')
            
            return ", ".join(t.title for t in record.contact_group.all())
    
    class Meta:
        model = ReminderMessaging
        fields = ['title','custom_data_namespace','contact_group','last_modified','table_model_action']
        
        
class RunningMessagesTable(tables.Table):
    
    class Meta:
        model = QueuedMessages
        fields = ['message','contact_dsoi','reminders','started_at']