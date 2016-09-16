'''
Created on Sep 16, 2016

@author: Dayo
'''

import logging

from .models import SMSDeliveryReportTransaction, SMSDeliveryReport

def process_deliveryreport_transaction():
    
    # get all unprocessed report transactions
    all_unprocessed_rt = SMSDeliveryReportTransaction.objects.filter(status='0')
    
    for u_rt in all_unprocessed_rt:
        
        message_id = u_rt.body['results']['messageId']
        message_status = u_rt.body['results']['status']['groupId']
        error_status = u_rt.body['results']['error']['groupId']
        
        SMSDeliveryReport.objects.filter(pk=message_id).update(msg_status=message_status,
                                                               msg_error=error_status
                                                               )
        
        # now update the status of the SMS delivery report transaction.
        u_rt.status = '1'
        u_rt.save()