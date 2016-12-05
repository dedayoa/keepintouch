'''
Created on Sep 16, 2016

@author: Dayo
'''

import logging
import arrow

from .models import SMSDeliveryReportTransaction, SMSDeliveryReport, EmailReportTransaction, EmailDeliveryReport,\
                    EmailReceiverAction

def process_sms_deliveryreport_transaction():
    
    # get all unprocessed report transactions
    all_unprocessed_rt = SMSDeliveryReportTransaction.objects.filter(status='0')
    
    for u_rt in all_unprocessed_rt:
        
        for result in u_rt.body['results']:
            message_id = result['messageId']
            message_status = result['status']['groupId']
            error_status = result['error']['groupId']
            
            SMSDeliveryReport.objects.filter(pk=message_id).update(msg_status=message_status,
                                                                   msg_error=error_status
                                                                   )
            
        # now update the status of the SMS delivery report transaction.
        u_rt.status = '1'
        u_rt.save()
        
        
def process_email_deliveryreport_transaction():
    
    def email_event_fxn(email_dr_id, email_status, sent_at=0):
        
        # email is sent (actually processed from far end) and sent_at is not 0
        if email_status=='0' and sent_at != 0:
            # convert unix timestamp to utc datetune
            sent_at_pydt = arrow.get(sent_at).datetime
             
            EmailDeliveryReport.objects.filter(id=email_dr_id).update(
                    msg_status = email_status,
                    sent_at = sent_at_pydt
                    )
        else:
            EmailDeliveryReport.objects.filter(id=email_dr_id).update(
                    msg_status = email_status
                    )
    
    def recepient_action_fxn(email_dr_id, action_id, action_timestamp, report):
        
        # convert unix timestamp to utc datetune
        action_t = arrow.get(action_timestamp).datetime
        
        edr_obj = EmailDeliveryReport.objects.get(id=email_dr_id)
        
        EmailReceiverAction.objects.create(
                    email_delivery_report = edr_obj,
                    action = action_id,
                    action_time = action_t,
                    extra_data = report
                    )
    
    # get all unprocessed report transactions
    all_unprocessed_edr = EmailReportTransaction.objects.filter(status='0')
    
    for edr in all_unprocessed_edr:
        
        for report in edr.body:
            if report['event'] == 'delivered':
                email_event_fxn(report['email_id'],EmailDeliveryReport.E_DELIVERED)
            if report['event'] == 'processed':
                email_event_fxn(report['email_id'],EmailDeliveryReport.E_SENT, sent_at=report['timestamp'])
            if report['event'] == 'dropped':
                email_event_fxn(report['email_id'],EmailDeliveryReport.E_DROPPED)
            if report['event'] == 'bounced':
                email_event_fxn(report['email_id'],EmailDeliveryReport.E_BOUNCED)
            if report['event'] == 'deferred':
                email_event_fxn(report['email_id'],EmailDeliveryReport.E_DEFERRED)
            
            if report['event'] == 'open':
                recepient_action_fxn(report['email_id'], 1, report['timestamp'],report)
            if report['event'] == 'click':
                recepient_action_fxn(report['email_id'], 2, report['timestamp'],report)
            if report['event'] == 'spamreport':
                recepient_action_fxn(report['email_id'], 7, report['timestamp'],report)
            
        # now update the status of the SMS delivery report transaction.
        edr.status = '1'
        edr.save()