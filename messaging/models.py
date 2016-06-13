import datetime
import html2text

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from core.models import KITUser, Contact, SMTPSetting, ContactGroup, MessageTemplate

from model_utils.fields import StatusField, MonitorField
from model_utils import Choices
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


def get_default_time():
    return timezone.now()+datetime.timedelta(seconds=settings.MSG_WAIT_TIME)

class StandardMessaging(models.Model):
    
    STATUS = Choices('draft', 'waiting', 'processed')
    
    email_message = models.TextField(blank=True)
    sms_message = models.TextField(blank=True)
    send_sms = models.BooleanField(verbose_name="Send SMS")
    send_email = models.BooleanField(verbose_name="Send Email")
    recipients = models.ManyToManyField(Contact)
    delivery_time = models.DateTimeField(default=get_default_time, verbose_name = "Deliver at")
    
    smtp_setting = models.ForeignKey(SMTPSetting, null=True, blank=True)
    sms_sender = models.CharField(max_length=11, blank=True)
    
    
    created_by = models.ForeignKey(KITUser, models.PROTECT)
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    status = StatusField()
    #waiting_at = MonitorField(monitor='status', when=['waiting'])
    processed_at = MonitorField(monitor='status', when=['processed'])
    

    def __str__(self):
        if self.send_sms:
            return "{}...".format(self.sms_message[0:25])
        elif self.send_email:
            return "{}...".format(html2text.html2text(self.email_message)[0:35])
            
            
    
    def get_absolute_url(self):
        return reverse('messaging:standard-message-draft',args=[self.pk]) 
    
    
class AdvancedMessaging(models.Model):
    
    STATUS = Choices('draft', 'waiting', 'processed')
    
    title = models.CharField(max_length=100, blank=False)
    message_template = models.ForeignKey(MessageTemplate, blank=False)
    contact_group = models.ManyToManyField(ContactGroup)
    delivery_time = models.DateTimeField(default=get_default_time, verbose_name = "Deliver at")
       
    created_by = models.ForeignKey(KITUser, models.PROTECT)
    
    status = StatusField()
    #waiting_at = MonitorField(monitor='status', when=['waiting'])
    processed_at = MonitorField(monitor='status', when=['processed'])
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
            
    def get_absolute_url(self):
        return reverse('messaging:advanced-message-draft',args=[self.pk]) 
    

class ProcessedMessages(models.Model):
    
    MSG_TYPE = (
        ('ADVANCED',' Advanced'),
        ('STANDARD',' Standard')
                )
    
    message_type = models.CharField(max_length=10, choices=MSG_TYPE)
    message = JSONField()
    message_id = models.IntegerField()
    
    created_by = models.ForeignKey(KITUser, models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "{} Message {}".format(self.message_type,self.message_id)
    
    def get_absolute_url(self):
        return None