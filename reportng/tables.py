'''
Created on Aug 3, 2016

@author: Dayo
'''

import os, json
import re
import arrow

import django_tables2 as tables
from django_tables2.utils import A
from django.utils.safestring import mark_safe
from django.utils.html import format_html, html_safe

from .models import SMSDeliveryReport, SMSDeliveryReportHistory, EmailDeliveryReport, CallDetailReport,\
                    EmailReceiverAction
from django.core.urlresolvers import reverse, reverse_lazy

import html2text
from cacheops import cached_as



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
    from_email = tables.Column(verbose_name="From")
    to_email = tables.EmailColumn(verbose_name="To")
    msg_status = tables.Column(verbose_name='Status')
    sent_at = tables.Column(verbose_name="Sent", attrs={'td': {'style':'width:80px; white-space: nowrap; font-size: 9pt;'}})
    activity = tables.Column(verbose_name="Activity", accessor='pk', attrs={'td': {'style':'width:130px; white-space: nowrap'}})
    
    
    def __init__(self, *args, **kwargs):
        self.utz = kwargs.pop('utz')
        super(EmailReportTable, self).__init__(*args, **kwargs)
    
    @cached_as(timeout=120)
    def render_activity(self, record):
        
        ev_open = EmailReceiverAction.objects.filter(email_delivery_report = record.pk, action= '1')
        ev_click = EmailReceiverAction.objects.filter(email_delivery_report = record.pk, action= '2')
        ev_spam_report = EmailReceiverAction.objects.filter(email_delivery_report = record.pk, action= '7')
        
        return format_html(''+
                '<span data-tooltip aria-haspopup="true" class="has-tip circle '+("kt-e-activity-open" if ev_open else "kt-e-inactivity")+'" title="Open: {}">O</span>'+
                '<span data-tooltip aria-haspopup="true" class="has-tip circle '+("kt-e-activity-click" if ev_click else "kt-e-inactivity")+'" title="Click: {}">C</span>'+
                '<span data-tooltip aria-haspopup="true" class="has-tip circle '+("kt-e-activity-spamr" if ev_spam_report else "kt-e-inactivity")+'" title="Spam Report: {}">R</span>',
                "" if not ev_open else (arrow.get(ev_open[0].action_time).to(self.utz).format('DD-MM-YYYY HH:mm')).datetime,
                "" if not ev_click else (arrow.get(ev_click[0].action_time).to(self.utz).format('DD-MM-YYYY HH:mm')).datetime,
                "" if not ev_spam_report else (arrow.get(ev_spam_report[0].action_time).to(self.utz).format('DD-MM-YYYY HH:mm')).datetime
                )
    
    
    def render_email_message(self, record):
        return format_html('<a href="#">{}</a>',text_2_wordlist(html_to_text(record.email_message.get('title')), 5))
    
    class Meta:
        model = EmailDeliveryReport
        fields = ('email_message','from_email','to_email','msg_status','sent_at','activity')
        empty_text = 'There are no Reports to display.'
        attrs = {'style': 'width: 100%'}


        
        
class CallReportTable(tables.Table):
    
    a_leg_call_start = tables.DateTimeColumn(verbose_name='Time')
    b_leg_called_number = tables.Column(verbose_name='Called Number')
    get_total_billable_call_duration = tables.Column(verbose_name='Duration')
    total_call_cost = tables.Column(verbose_name='Debit')
    
    def render_total_call_cost(self, record):
        return "{} {}".format(record.total_call_cost.gross, record.total_call_cost.currency)
    
    def render_get_total_billable_call_duration(self, record):
        m, s = divmod(record.get_total_billable_call_duration(), 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)
    
    def render_b_leg_called_number(self, record):
        return mark_safe('<div>{}<br/><small style="color: #444">{}</small></div>'.format(record.b_leg_called_number, record.b_leg_callerid))
    
    
    class Meta:
        model = CallDetailReport
        fields = ('a_leg_call_start','b_leg_called_number','get_total_billable_call_duration','total_call_cost')
        empty_text = 'There are no Reports to display.'
        attrs = {'style': 'width: 100%'}