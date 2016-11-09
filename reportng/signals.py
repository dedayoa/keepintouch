'''
Created on Nov 9, 2016

@author: Dayo
'''
from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save
import arrow

from .models import CallDetailReportTransaction, CallDetailReport

@receiver(post_save, sender=CallDetailReportTransaction)
def process_cdr_transaction(sender, instance, **kwargs):
    if kwargs.get('created', False):
        
        def on_commit():
            if instance.body['variables']['leg'] == '1' or 'A':                
                cdra = CallDetailReport.objects.get(id=instance.body['variables']['uuid'])
                 
                cdra.a_leg_billsec = instance.body['variables']['billsec'],
                cdra.a_leg_callerid = instance.body['callflow']['caller_profile']['caller_id_name'],
                cdra.a_leg_called_number = instance.body['callflow']['caller_profile']['destination_number'],
                cdra.a_leg_call_start = arrow.get(instance.body['variables']['start_epoch']).datetime,
                cdra.a_leg_uuid = instance.call_uuid
                
                cdra.save()
            
            elif instance.body['variables']['leg'] == '2' or 'B':
                cdrb = CallDetailReport.objects.get(id=instance.body['variables']['uuid'])
                
                cdrb.b_leg_billsec = instance.body['variables']['billsec'],
                cdrb.b_leg_callerid = instance.body['callflow']['caller_profile']['caller_id_name'],
                cdrb.b_leg_called_number = instance.body['callflow']['caller_profile']['destination_number'],
                cdrb.b_leg_call_start = arrow.get(instance.body['variables']['start_epoch']).datetime,
                cdrb.b_leg_uuid = instance.call_uuid
                
                cdrb.save()
                
            instance.status = '1'
            instance.save()
                
        transaction.on_commit(on_commit)   