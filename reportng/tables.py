'''
Created on Aug 3, 2016

@author: Dayo
'''

import os, json

import django_tables2 as tables
from django_tables2.utils import A
from django.utils.safestring import mark_safe
from django.utils.html import format_html, html_safe

from .models import SMSDeliveryReport, SMSDeliveryReportHistory
from django.core.urlresolvers import reverse, reverse_lazy




class SMSReportTable(tables.Table):
    
    sms_message = tables.Column(verbose_name='Message')
    sms_sender = tables.Column(verbose_name='Sender')
    to_phone = tables.Column(verbose_name='Recipient')
    msg_status = tables.Column(verbose_name='Status')
    msg_error = tables.Column(verbose_name='Error')
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
        
    
    class Meta:
        model = SMSDeliveryReport
        fields = ('sms_message','sms_sender','to_phone','msg_status','msg_error','created')
        empty_text = 'There are no Reports to display.'
        attrs = {'style': 'width: 100%'}