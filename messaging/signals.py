'''
Created on Aug 24, 2016

@author: Dayo
'''

from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.apps import apps
from django.utils import timezone

from .models import IssueFeedback
from .tasks import process_issue_submission_notification, process_verification_messages

from core.models import KITActivationCode

        

@receiver(post_save, sender=IssueFeedback)
def send_email_to_sender_and_dev_channel(sender, instance, **kwargs):
    if kwargs.get('created', False):
        #send thankyou email to submitter
        #send notification to dev channel
        try:
            isu = instance.screenshot.url
        except ValueError:
            isu = None
        
        def on_commit():
            fullname = instance.submitter.user.get_full_name()
            print(fullname)
            process_issue_submission_notification(
                    fullname = fullname,
                    submitter_email = instance.submitter.user.email,
                    title = instance.title,
                    detail = instance.detail,
                    attachment = isu,
                    submitter_kusr = instance.submitter
                                        )
        transaction.on_commit(on_commit)     
        
        
            
            
@receiver(post_save, sender=KITActivationCode)
def process_sending_verification_details(sender, instance, **kwargs):
    if kwargs.get('created', False):
        #send email or sms
        def on_commit():
            fullname = instance.user.get_full_name()
            kituser = instance.user.kituser
            phone_validated = instance.user.kituser.phone_validated
            email_validated = instance.user.kituser.email_validated
            phone_number = instance.user.kituser.phone_number
            email = instance.user.email
            phone_verification_code = instance.user.kitactivationcode.phone_activation_code
            email_verification_code = instance.user.kitactivationcode.email_activation_code
            
            process_verification_messages(
                    fullname = fullname,
                    kuser = kituser,
                    phone_is_validated = phone_validated,
                    email_is_validated = email_validated,
                    phone_number = phone_number,
                    email = email,
                    phone_verification_code = phone_verification_code,
                    email_verification_code = email_verification_code,
                                        )
        transaction.on_commit(on_commit)
   

'''
    
@receiver(post_save, sender=User)
def create_required_info_for_free_user_registeration(sender, instance, **kwargs):
    if kwargs.get('created', False):
        #send email or sms
        def on_commit():
            KITUser.objects.create(user=instance, is_admin=True)
            # the above creates kitsystem,
            free_service_plan = KITServicePlan.objects.get(id=settings.FREE_SERVICE_PLAN_ID)
            kitbilling = apps.get_model('gomez', 'KITBilling')
            kitbilling.objects.create(
                    kit_admin=instance.kituser,
                    service_plan = free_service_plan,
                    next_due_date = arrow.utcnow().replace(years=+1).datetime.date(),
                    registered_on = timezone.now().date(),
                    account_status = 'AC'
                    )
            
        transaction.on_commit(on_commit)'''