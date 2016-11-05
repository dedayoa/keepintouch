'''
Created on Jun 10, 2016

@author: Dayo
'''

import django_tables2 as tables
from django_tables2.utils import A

from .models import StandardMessaging, AdvancedMessaging, ProcessedMessages, QueuedMessages,\
                    ReminderMessaging, FailedEmailMessage, FailedSMSMessage, FailedKITMessage,\
                    RunningMessage
from django.utils.html import format_html_join, format_html
from django.utils.safestring import mark_safe

from django.utils.translation import ugettext_lazy as _

import json
import re
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse

from .helper import text_2_wordlist



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
            return format_html('<span data-tooltip aria-haspopup="true" class="has-tip" data-disable-hover="false" tabindex=1 title="{}">{}</span>',\
                               record.__str__(),
                               #nltk.sent_tokenize(record.title)[0:5].join(" ")
                               text_2_wordlist(record.title, 3)
                               )
            
    class Meta:
        model = StandardMessaging
        fields = ('title','recipients','sms_sender','last_modified','table_model_action')
        empty_text = "There are no Draft Standard Messages to display"
        
        
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
        empty_text = "There are no Draft Advanced Messages to display"
        
        
class ProcessedMessagesTable(tables.Table):
    
    message = tables.Column(verbose_name="Message")
    message_type = tables.Column("Type")
    processed_at = tables.DateTimeColumn(verbose_name="Processed at")
    
    def render_message(self, record):
        
        serialized_m = json.dumps(record.message)
        #rex = re.compile('\\r|\\n')
        #re.sub(rex,'',aoi)
        
        return mark_safe('<a href="#" class="show-message-modal">{1} <span class="table-rowid-span">{2}</span><script type="application/json">{0}</script></a>'.\
            format(serialized_m, (record.message)['title'],'- %s'%(record.message)['others'].get('draft_title') if (record.message)['others'].get('draft_title') else ''))
    
    class Meta:
        model = ProcessedMessages
        fields = ['message','message_type','processed_at']
        empty_text = "There are no Processed Messages"
        
        
class QueuedMessagesTable(tables.Table):
    
    class Meta:
        model = QueuedMessages
        fields = ['message','message_type','delivery_time','message_id']
        empty_text = "There are no Queued Messages to display"


    
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
            return format_html('<span data-tooltip aria-haspopup="true" class="has-tip" data-disable-hover="false" tabindex=1 title="{}">{}</span>',\
                               record.__str__(),text_2_wordlist(record.title, 3)
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
        empty_text = "There are no Draft Reminder Messages to display"
        
        
class RunningMessagesTable(tables.Table):
    
    message = tables.Column(verbose_name="Message")
    contact_dsoi = tables.Column(verbose_name="Dates of Interest")
    reminders = tables.Column(verbose_name="Reminders")
    started_at = tables.Column(verbose_name="Started")
    
    class Meta:
        model = RunningMessage
        fields = ['message','contact_dsoi','reminders','started_at']
        empty_text = "There are no Running Messages to display"
        

class FailedKITMessagesTable(tables.Table):
    
    #message_data = tables.Column(verbose_name="Message")
    
    #def render_record_action(self, record):
    #    return format_html('<a class="button" href="{}">Retry</a>',record.get_absolute_url())
    
    '''
    def render_message_data(self, record):
        
        msg_data = record.message_data[0]
        
        if record.message_category == 'queued_msg':
            return msg_data.message.get('title')
        elif record.message_category == 'running_msg':
            return msg_data.'''
        
    
    class Meta:
        model = FailedKITMessage
        fields = ('message_category','reason','created','retries')
        empty_text = "There are no Failed Messages to display"
        
class FailedSMSMessagesTable(tables.Table):
    
    
    record_action = tables.LinkColumn(verbose_name="", \
                                       text=mark_safe('<span class="button small">Retry</span>'), \
                                       args=[A('pk')])
    
    sms_pickled_data = tables.Column(verbose_name='Message')
    retries = tables.Column(verbose_name="Retries")
    reason = tables.Column(verbose_name="Reason")

    def render_sms_pickled_data(self, record):
        return format_html('<span data-tooltip aria-haspopup="true" class="has-tip" data-disable-hover="false"'+ 
                            'tabindex=1 title="{}">SMS</span> from {} to {}',record.sms_pickled_data[1],\
                            record.sms_pickled_data[0], record.sms_pickled_data[2]
                           )
        

    created = tables.DateTimeColumn(verbose_name='Failed')
    
    class Meta:
        model = FailedSMSMessage
        fields = ('sms_pickled_data','reason','retries','created','record_action')
        empty_text = "There are no Failed SMS Messages to display"
        
class FailedSMSMessagesTable_Admin(tables.Table):
    
    sms_pickled_data = tables.Column(verbose_name='Message')
    retries = tables.Column(verbose_name="Retries")
    reason = tables.Column(verbose_name="Reason")
    owned_by = tables.Column(verbose_name="Owner")

    def render_sms_pickled_data(self, record):
        return format_html('<span data-tooltip aria-haspopup="true" class="has-tip" data-disable-hover="false"'+ 
                            'tabindex=1 title="{}">SMS</span> from {} to {}',record.sms_pickled_data[1],\
                            record.sms_pickled_data[0], record.sms_pickled_data[2]
                           )
        

    created = tables.DateTimeColumn(verbose_name='Failed')
    
    class Meta:
        model = FailedSMSMessage
        fields = ('sms_pickled_data','reason','retries','owned_by','created')
        empty_text = "There are no Failed SMS Messages to display"
    
        
        
class FailedEmailMessagesTable(tables.Table):

    record_action = tables.LinkColumn(verbose_name="", \
                                       text=mark_safe('<span class="button small">Retry</span>'), \
                                       args=[A('pk')])
        
    email_pickled_data = tables.Column(verbose_name='Message')
    retries = tables.Column(verbose_name="Retries")
    reason = tables.Column(verbose_name="Reason")
    
    created = tables.DateTimeColumn(verbose_name='Failed')
    
    def render_email_pickled_data(self, record):
        return format_html('<span data-tooltip aria-haspopup="true" class="has-tip" data-disable-hover="false"'+ 
                            'tabindex=1 title="{}">Email</span> from {} to {}',record.email_pickled_data[0][1],\
                            record.email_pickled_data[1], record.sms_pickled_data[0][2]
                           )
        
    class Meta:
        model = FailedEmailMessage
        fields = ('email_pickled_data','reason','retries','created','record_action')
        empty_text = "There are no Failed Email Messages to display"
        
        
class FailedEmailMessagesTable_Admin(tables.Table):

    record_action = tables.LinkColumn(verbose_name="", \
                                       text=mark_safe('<span class="button small">Retry</span>'), \
                                       args=[A('pk')])
        
    email_pickled_data = tables.Column(verbose_name='Message')
    retries = tables.Column(verbose_name="Retries")
    reason = tables.Column(verbose_name="Reason")
    
    created = tables.DateTimeColumn(verbose_name='Failed')
    owned_by = tables.Column(verbose_name="Owner")
    
    def render_email_pickled_data(self, record):
        return format_html('<span data-tooltip aria-haspopup="true" class="has-tip" data-disable-hover="false"'+ 
                            'tabindex=1 title="{}">Email</span> from {} to {}',record.email_pickled_data[0][1],\
                            record.email_pickled_data[1], record.sms_pickled_data[0][2]
                           )
        
    class Meta:
        model = FailedEmailMessage
        fields = ('email_pickled_data','reason','retries','owned_by','created')
        empty_text = "There are no Failed Email Messages to display"
        
        
      
