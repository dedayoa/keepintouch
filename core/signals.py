'''
Created on Aug 29, 2016

@author: Dayo
'''
import sys
from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import KITUser, KITUBalance, CoUserGroup
from django.apps import apps
from django.utils import timezone


@receiver(post_save, sender=KITUser)
def create_kituser_assoc_tables(sender, instance, **kwargs):
    if kwargs.get('created', False):
        def on_commit():
            kitbilling = apps.get_model('gomez', 'KITBilling')
            kitsystem = apps.get_model('gomez', 'KITSystem')
            
            kitbilling.objects.create(
                    kit_admin=instance,
                    next_due_date = timezone.now().date(),
                    registered_on = timezone.now().date()
                    )
            kitsystem.objects.create(kit_admin=instance)
            
            KITUBalance.objects.create(kit_user=instance)
            
        transaction.on_commit(on_commit) 

 
@receiver(post_save, sender=KITUser)
def create_and_set_default_user_group(sender, instance, *args, **kwargs):
    
    if instance.is_admin:
        
        #if not CoUserGroup.objects.filter(title='Default', kit_admin=instance).exists():
        
        kitadmin = KITUser.objects.get(pk=instance.id)
        
        try:
            coug, created = CoUserGroup.objects.get_or_create(
                    title = 'Default',
                    description = 'Default User Group',
                    kit_admin = kitadmin,
                    defaults = {
                        'active' : True
                                }
                )
            if created:
                instance.user_group = coug
        except:
            print("Error:", sys.exc_info())
  