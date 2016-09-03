from django.db import models

# Create your models here.

from django.core.urlresolvers import reverse

from randomslugfield.fields import RandomSlugField
from django.contrib.postgres.fields.jsonb import JSONField
from country_dialcode.models import Prefix

from django.utils.translation import ugettext_lazy as _
from model_utils.fields import StatusField, MonitorField
from model_utils import Choices

from phonenumber_field.modelfields import PhoneNumberField
    
    
class KITServicePlan(models.Model):
    name = models.CharField(max_length=100)
    free_sms = models.BooleanField(default=False, help_text="Weekly Free SMS?")
    free_sms_units = models.PositiveIntegerField(help_text="Number of Weekly Free SMS", default=0)
    user_accounts_allowed = models.PositiveIntegerField(default=0)
    user_groups_allowed = models.PositiveIntegerField(default=0)
    can_use_custom_data = models.BooleanField(default=False)
    api_access = models.BooleanField(default=False)
    sms_unit_bundle = models.PositiveIntegerField(default=0)
    data_collection_capacity = models.PositiveIntegerField(default=0)

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
    
    kit_admin = models.OneToOneField('core.KITUser', limit_choices_to={'is_admin':True})
    next_due_date = models.DateField()
    registered_on = models.DateField()
    service_plan = models.ForeignKey(KITServicePlan, blank=True, null=True)
    billing_cycle = models.CharField(max_length=2, choices=BILL_CY, default='AN')
    account_status = models.CharField(max_length=2, choices=ACCT_STATUS, default='PE')
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)            
    
    class Meta:
        verbose_name = 'Billing'
        
    def __str__(self):
        return "{} {}".format(self.kit_admin.user.first_name,self.kit_admin.user.last_name)
    
    
class KITSystem(models.Model):
    # SaaS user "system" model
    # Where a user can define account/system specific settings
    
    kit_admin = models.OneToOneField('core.KITUser', limit_choices_to={'is_admin':True}, null=True)
    company_wide_contacts = models.BooleanField(verbose_name="Organisation-wide Contacts",\
                                                help_text="Check if you want all users to see contacts from all groups",\
                                                default=True)
    
    last_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "{} {}".format(self.kit_admin.user.first_name,self.kit_admin.user.last_name)
    
    
    def get_absolute_url(self):
        return reverse('gomez:system-settings',args=[self.pk])

    
    
class SMSRateTable(models.Model):
    
    dialcode = models.ForeignKey(Prefix, verbose_name=_("Destination"), help_text=_("Select Prefix"))
    sms_units = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return str(self.dialcode)
    
    
    
        
        
class SMSReport(models.Model):
    
    STATUS = (
        (0,'Delivered'),
        (1,'Accepted'),
        (2,'Expired'),
        (3,'Undelivered'),
        (4,'Rejected'),
              )
    
    to_phone = PhoneNumberField(blank=False)
    gw_msg_id = models.CharField(max_length=255, blank=True, null=True)
    sms_message = JSONField() #body, messageid,
    sms_gateway = JSONField()
    status = StatusField()
    
    owner = models.ForeignKey('core.KITUser', models.PROTECT)
    last_modified = models.DateTimeField(auto_now=True)
    
    #datetime sms was sent,which may be different from when it entered the processing queue
    created = models.DateTimeField(auto_now_add=True)  
    
    def __str__(self):
        return "SMS to {}".format(self.to_phone.as_international)
    
    
class EmailReport(models.Model):
    
    STATUS = (
        (0,'Sent'),
        (1,'Delivered'),
        (2,'Deferred'),
        (3,'Bounce'),
        #(4,'Spam Report'),
              )
    
    status = StatusField()
    to_email = models.EmailField()
    from_email = models.EmailField()
    email_message = JSONField()
    email_gateway = JSONField()
    
    owner = models.ForeignKey('core.KITUser', models.PROTECT)
    last_modified = models.DateTimeField(auto_now=True)
    
    #datetime email was sent,which may be different from when it entered the processing queue
    created = models.DateTimeField(auto_now_add=True)  
    
    
    def __str__(self):
        return "Email from {} to {}".format(self.from_email,self.to_email)