'''
Created on Aug 3, 2016

@author: Dayo
'''

import os, json
import re

import django_tables2 as tables
from django_tables2.utils import A
from django.utils.safestring import mark_safe
from django.utils.html import format_html, html_safe

from .models import SMSDeliveryReport, SMSDeliveryReportHistory, EmailDeliveryReport
from django.core.urlresolvers import reverse, reverse_lazy

import html2text




def text_2_wordlist(text, max_number_of_words):
    text_list = re.sub("[^\w]", " ",  text).split()
    return " ".join(text_list[0:max_number_of_words])+"..." if len(text_list) > max_number_of_words else text


def html_to_text(htmlmsg):    
    jtext = html2text.HTML2Text()
    jtext.ignore_links = True
    jtext.ignore_tables = True
    jtext.ignore_anchors = True
    return jtext.handle(htmlmsg)


class SMSReportTable(tables.Table):
    
    sms_message = tables.Column(verbose_name='Message', orderable=False)
    sms_sender = tables.Column(verbose_name='Sender')
    to_phone = tables.Column(verbose_name='Recipient')
    msg_info = tables.Column(verbose_name='Delivery Info', accessor='pk', orderable=False)
    created = tables.Column(verbose_name='Sent')
    
    
    def render_sms_message(self, record):
        '''
        
        <span data-sms={} data-sms-history={} >Dear Sayo, This is my mail...</span>
        
        '''

        sms_message = json.dumps(record.sms_message)
        del_hist = record.smsdeliveryreporthistory_set.order_by('created').values('data','created')
        for qsi in del_hist:
            qsi['created'] = qsi['created'].isoformat()
        
        sms_history = json.dumps(list(del_hist))
        smsm_text = record.sms_message['text'][:25] + (record.sms_message['text'][25:] and '...')
        return mark_safe('<a href="#" class="sms-delivery-detail" data-sms=\'{}\' data-sms-history=\'{}\'>{}</a>'.format(sms_message, sms_history,smsm_text))
        
    
    def render_msg_info(self, record):
        return format_html('<div style="font-size: 80%"><div>Status: <strong>{}</strong></div><div>Error: <strong>{}</strong></div></div>',record.get_msg_status_display(), record.get_msg_error_display())
        

    
    class Meta:
        model = SMSDeliveryReport
        fields = ('sms_message','sms_sender','to_phone','msg_info','created')
        empty_text = 'There are no Reports to display.'
        attrs = {'style': 'width: 100%'}


        
class EmailReportTable(tables.Table):
    
    email_message = tables.Column(verbose_name='Email')
    from_email = tables.EmailColumn(verbose_name="From")
    to_email = tables.EmailColumn(verbose_name="To")
    msg_status = tables.Column(verbose_name='Status')
    created = tables.Column(verbose_name="Sent")
    
    
    def render_email_message(self, record):
        return format_html('<a href="#">{}</a>',text_2_wordlist(html_to_text(record.email_message.get('title')), 5))
    
    class Meta:
        model = EmailDeliveryReport
        fields = ('email_message','from_email','to_email','msg_status','created')
        empty_text = 'There are no Reports to display.'
        attrs = {'style': 'width: 100%'}