'''
Created on Jun 10, 2016

@author: Dayo
'''

import django_tables2 as tables
from django_tables2.utils import A

from .models import StandardMessaging
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from django.utils.translation import ugettext_lazy as _

class DraftStandardMessagesTable(tables.Table):
    
    __str__ = tables.Column(verbose_name="Message")
    recipients = tables.Column(verbose_name=_("Recipients"))
    delivery_time = tables.DateTimeColumn()
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
        fields = ('__str__','recipients','delivery_time','sms_sender','table_model_action')
    