from django.db import models, transaction

# Create your models here.

from core.models import KITUser
from django.core.urlresolvers import reverse

from django.dispatch import receiver
from django.db.models.signals import post_save
        
from messaging.tasks import process_system_notification

    
    
class KITServicePlan(models.Model):
    name = models.CharField(max_length=100)
        
    def __str__(self):
        return self.name
    
    
class KITBilling(models.Model):

    
    ACCT_STATUS = (
        ('PE','Pending'),
        ('AC','Active'),
        ('SU','Suspended'),
        ('TE','Terminated'),
        ('CA','Cancelled'),
        ('FR','Fraud'),
        )

    BILL_CY = (
        ('QU', 'Quarterly'),
        ('AN', 'Annually'),
               )
    
    kit_admin = models.OneToOneField(KITUser, limit_choices_to={'is_admin':True})
    next_due_date = models.DateField()
    registered_on = models.DateField()
    service_plan = models.ForeignKey(KITServicePlan)
    billing_cycle = models.CharField(max_length=2, choices=BILL_CY, default='AN')
    account_status = models.CharField(max_length=2, choices=ACCT_STATUS, default='PE')
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Billing'
        
    def __str__(self):
        return "{} {}".format(self.kit_admin.user.first_name,self.kit_admin.user.last_name)
    
    
class KITSystem(models.Model):

    
    kit_admin = models.OneToOneField(KITUser, limit_choices_to={'is_admin':True}, null=True)
    company_wide_contacts = models.BooleanField(verbose_name="Organisation-wide Contacts",\
                                                help_text="Check if you want all users to see contacts from all groups")
    
    last_modified = models.DateTimeField(auto_now=True)
    
    
    def get_absolute_url(self):
        return reverse('gomez:system-settings',args=[self.pk])


class IssueFeedback(models.Model):
    title = models.CharField(max_length=150, blank=False)
    detail = models.TextField(blank=False)
    screenshot = models.ImageField(upload_to="issue_feedback/", blank=True)
    
    resolution_flag = models.BooleanField()
    
    submitter = models.ForeignKey(KITUser, on_delete=models.SET_NULL, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    
    
@receiver(post_save, sender=IssueFeedback)
def send_email_to_sender_and_dev_channel(sender, instance, **kwargs):
    if kwargs.get('created', False):
        #send thankyou email to submitter
        #send notification to dev channel
        def on_commit():
            fullname = "{} {}".format(instance.submitter.user.first_name,instance.submitter.user.last_name)
            process_system_notification(
                    fullname = fullname,
                    submitter_email = instance.submitter.user.email,
                    title = instance.title,
                    detail = instance.detail,
                    attachment = getattr(instance,'screenshot.url',''),
                    submitter_kusr = instance.submitter
                                        )
            print(fullname)
        transaction.on_commit(on_commit)    