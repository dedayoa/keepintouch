from django.db import models, transaction

# Create your models here.

from core.models import KITUser, MessageTemplate, Contact
from django.core.urlresolvers import reverse

from django.dispatch import receiver
from django.db.models.signals import post_save
        
from messaging.tasks import process_system_notification
from randomslugfield.fields import RandomSlugField
from django.contrib.postgres.fields.jsonb import JSONField

    
    
class KITServicePlan(models.Model):
    name = models.CharField(max_length=100)
    ad_supported = models.BooleanField(default=False)
    free_sms = models.BooleanField(default=False, help_text="Weekly Free SMS?")
    free_sms_units = models.PositiveIntegerField(help_text="Number of Weekly Free SMS", default=0)
    user_accounts_allowed = models.PositiveIntegerField(default=0)
    user_groups_allowed = models.PositiveIntegerField(default=0)
    can_use_custom_data = models.BooleanField(default=False)
    api_access = models.BooleanField(default=False)
    sms_unit_bundle = models.PositiveIntegerField(default=0)

        
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
    service_plan = models.ForeignKey(KITServicePlan, blank=True, null=True)
    billing_cycle = models.CharField(max_length=2, choices=BILL_CY, default='AN')
    account_status = models.CharField(max_length=2, choices=ACCT_STATUS, default='PE')
    is_full_admin = models.BooleanField(default=False)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
        
    def save(self, *args, **kwargs):
        if self.service_plan.ad_supported and self.service_plan.user_groups_allowed == 0:
            self.is_full_admin = False
        super(KITBilling, self).save(*args, **kwargs)
            
    
    class Meta:
        verbose_name = 'Billing'
        
    def __str__(self):
        return "{} {}".format(self.kit_admin.user.first_name,self.kit_admin.user.last_name)
    
    
class KITSystem(models.Model):

    
    kit_admin = models.OneToOneField(KITUser, limit_choices_to={'is_admin':True}, null=True)
    company_wide_contacts = models.BooleanField(verbose_name="Organisation-wide Contacts",\
                                                help_text="Check if you want all users to see contacts from all groups",\
                                                default=True)
    
    last_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "{} {}".format(self.kit_admin.user.first_name,self.kit_admin.user.last_name)
    
    
    def get_absolute_url(self):
        return reverse('gomez:system-settings',args=[self.pk])


class IssueFeedback(models.Model):
    title = models.CharField(max_length=150, blank=False)
    detail = models.TextField(blank=False)
    screenshot = models.ImageField(upload_to="issue_feedback/", blank=True)
    
    resolution_flag = models.BooleanField(default=False)
    
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
        try:
            isu = instance.screenshot.url
        except ValueError:
            isu = None
        
        def on_commit():
            fullname = "{} {}".format(instance.submitter.user.first_name,instance.submitter.user.last_name)
            process_system_notification(
                    fullname = fullname,
                    submitter_email = instance.submitter.user.email,
                    title = instance.title,
                    detail = instance.detail,
                    attachment = isu,
                    submitter_kusr = instance.submitter
                                        )
        transaction.on_commit(on_commit)
        
        
        
class InCal(models.Model):
    
    OPTIONS = (
        ('onetime','One Time'),
        ('recurring','Recurring'),
               )

    
    title = models.CharField(max_length=100)
    message_template = models.ForeignKey(MessageTemplate)
    start_date = models.DateTimeField()
    next_date = models.DateTimeField(blank=True)
    end_date = models.DateTimeField(blank=True)
    