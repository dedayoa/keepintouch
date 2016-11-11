'''
Created on Nov 9, 2016

@author: Dayo
'''

from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save
import arrow

from core.models import KITUBalance
from .models import CallDetailReportTransaction, CallDetailReport

@receiver(post_save, sender=CallDetailReportTransaction)
def process_cdr_transaction(sender, instance, **kwargs):
    if kwargs.get('created', False):        
        def on_commit():
            if instance.body['variables']['leg'] == '1':                
                CallDetailReport.objects.filter(id=instance.body['variables']['uuid']).update(
                            a_leg_billsec = instance.body['variables']['billsec'],
                            a_leg_callerid = instance.body['callflow'][0]['caller_profile']['caller_id_name'],
                            a_leg_called_number = instance.body['callflow'][0]['caller_profile']['destination_number'],
                            a_leg_call_start = arrow.get(instance.body['variables']['start_epoch']).datetime,
                            a_leg_uuid = instance.call_uuid
                            )
                kucdr = CallDetailReport.objects.get(id=instance.body['variables']['uuid'])
                kucdr.save()
                #ku = KITUser.objects.get(id=kuid)
                kubal = KITUBalance.objects.get(kit_user__id=kucdr.kituser_id)
                
                #deduct cost of call
                billsec = int(instance.body['variables']['billsec'])
                new_balance = kubal.user_balance - ((billsec*kucdr.a_leg_per_min_call_price)/60).gross
                
                # save new balance
                kubal.user_balance = new_balance
                kubal.save()
                
                
            
            elif instance.body['variables']['leg'] == '2':
                CallDetailReport.objects.filter(id=instance.body['variables']['uuid']).update(
                            b_leg_billsec = instance.body['variables']['billsec'],
                            b_leg_callerid = instance.body['callflow'][0]['caller_profile']['caller_id_name'],
                            b_leg_called_number = instance.body['callflow'][0]['caller_profile']['destination_number'],
                            b_leg_uuid = instance.call_uuid
                            )
                kucdr = CallDetailReport.objects.get(id=instance.body['variables']['uuid'])
                kucdr.save()
                #ku = KITUser.objects.get(id=kuid)
                kubal = KITUBalance.objects.get(kit_user__id=kucdr.kituser_id)
                
                #deduct cost of call
                billsec = int(instance.body['variables']['billsec'])
                new_balance = kubal.user_balance - ((billsec*kucdr.b_leg_per_min_call_price)/60).gross
                
                # save new balance
                kubal.user_balance = new_balance
                kubal.save()
                
                
            instance.status = '1'
            instance.save()
            
            # deduct from user balance
                
        transaction.on_commit(on_commit)   