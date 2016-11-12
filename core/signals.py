'''
Created on Aug 29, 2016

@author: Dayo
'''
import sys
import arrow

from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.apps import apps
from django.utils import timezone
from django.contrib.auth.models import Group, User
from django.conf import settings

from .models import KITUser, KITUBalance, CoUserGroup

from sitegate.signals import sig_user_signup_success
from gomez.models import KITServicePlan
from messaging.tasks import process_system_email_notification



@receiver(post_save, sender=KITUser)
def create_kituser_assoc_tables(sender, instance, **kwargs):
    if kwargs.get('created', False):
        def on_commit():
            kitbilling = apps.get_model('gomez', 'KITBilling')
            kitsystem = apps.get_model('gomez', 'KITSystem')
            
            kitbilling.objects.create(
                    kit_admin=instance,
                    last_renew_date = timezone.now().date(),
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
            


@receiver(sig_user_signup_success)                
def free_trial_user_signup_callback(signup_result, flow, request, **kwargs):
    if request.path == '/register/free-trial/':
        #disconnect the post_save signal for KITUser
        post_save.disconnect(create_kituser_assoc_tables, sender=KITUser)
        
        # create new KITUser
        KITUser.objects.create(user=signup_result, is_admin=True)
        
        # connect again
        post_save.connect(create_kituser_assoc_tables, sender=KITUser)
        

        free_trial_service_plan = KITServicePlan.objects.get(id=settings.FREE_TRIAL_SERVICE_PLAN_ID)
        
        kitbilling = apps.get_model('gomez', 'KITBilling')
        kitbilling.objects.create(
                kit_admin=signup_result.kituser,
                service_plan = free_trial_service_plan,
                next_due_date = arrow.utcnow().replace(days=settings.FREE_TRIAL_VALIDITY_PERIOD).datetime.date(),
                registered_on = timezone.now().date(),
                account_status = 'AC',
                last_renew_date = timezone.now().date()
                )
        
        kitsystem = apps.get_model('gomez', 'KITSystem')
        kitsystem.objects.create(kit_admin=signup_result.kituser)
        
        KITUBalance.objects.create(kit_user=signup_result.kituser, user_balance=settings.FREE_TRIAL_FREE_CREDIT)
        #set free user permissions
        group = Group.objects.get(id=settings.FREE_TRIAL_GROUP_PERMS_ID)
        signup_result.groups.add(group)


@receiver(post_save, sender=KITUser)
def send_new_user_created_by_kitadmin_welcome_email(sender, instance, created, *args, **kwargs):
    
    if created:
        if not instance.is_admin:
            '''
            Dear Adedayo,
            You have been signed up as a user of In.Touch by Tope Martins of Corp Global.
            In.Touch is a Business Messaging Automation Solution that organizes, manages and energizes your communication
            with the people that matter.
            To login, visit http://cloud.intouchng.com/
            Find Your Login Details Below:
            Username: dahzle
            Password: wiebe893
            We highly recommend that you change this password to something only you would know - and make sure it is also hard to guess.
            
            '''
            password = User.objects.make_random_password() #http://stackoverflow.com/a/9481049
            
            user = instance.user
            user.set_password(password)
            user.save()
            
            kadmin = instance.parent
            
            etemplate = 'core/email/new_kituser_account_created_email_with_default_password.html'
            et_context = {
                    'user_fullname' : user.get_full_name(),
                    'admin_fullname' : kadmin.user.get_full_name(),
                    'admin_organization' : kadmin.address.organization,
                    'user_username' : user.get_username(),
                    'user_password' : password                
                          }
            
            process_system_email_notification(
                        etemplate,
                        context_kwargs=et_context,
                        title='You Have Been Signed Up',
                        recipients=[user.email]
                                              )