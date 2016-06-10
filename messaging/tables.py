'''
Created on Jun 10, 2016

@author: Dayo
'''

import django_tables2 as tables
from django_tables2.utils import A

from .models import StandardMessaging

class StandardMessagingTable(tables.Table):
    
    message = tables.Column()
    recipients = tables.Column()
    delivery_time = tables.DateTimeColumn()
    status = tables.Column()
    sms_sender = tables.Column()
    
    def render_message(self):
        return "Message"
    
    class Meta:
        model = StandardMessaging
        fields = ('message','recipients','delivery_time','status','sms_sender')
    