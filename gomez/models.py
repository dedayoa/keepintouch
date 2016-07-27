from django.db import models

# Create your models here.

from core.models import KITUser
from django.core.urlresolvers import reverse
        


    
    
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
