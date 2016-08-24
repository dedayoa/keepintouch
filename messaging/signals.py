'''
Created on Aug 24, 2016

@author: Dayo
'''


from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import IssueFeedback
from .tasks import process_system_notification
        

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
            fullname = "{} {}".format(instance.submitter.user.first_name,instance.submitter.user.last_name)
            print(fullname)
            process_system_notification(
                    fullname = fullname,
                    submitter_email = instance.submitter.user.email,
                    title = instance.title,
                    detail = instance.detail,
                    attachment = isu,
                    submitter_kusr = instance.submitter
                                        )
        transaction.on_commit(on_commit)     