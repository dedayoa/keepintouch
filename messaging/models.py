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

from phonenumber_field.modelfields import PhoneNumberField


def get_default_time():
    return timezone.now()+datetime.timedelta(seconds=settings.MSG_WAIT_TIME)

class StandardMessaging(models.Model):
    
    STATUS = Choices('draft', 'waiting', 'processed')
    
    title = models.CharField(max_length=100, blank=False)
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
    #processed_at = MonitorField(monitor='status', when=['processed'])
    

    def __str__(self):
        if self.send_sms:
            sms_m = self.sms_message
            length = 75
            return ("S: {}...".format(sms_m[0:length]) if len(sms_m) > length else "{}".format(sms_m))
        elif self.send_email:
            email_m = html2text.html2text(self.email_message)
            length = 90
            return "{}...".format(email_m[0:length]) if len(email_m) > length else "{}".format(email_m)
            
            
    
    def get_absolute_url(self):
        return reverse('messaging:standard-message-draft',args=[self.pk])
    
    
    class Meta:
        verbose_name_plural = "Standard Messaging"
    
    
class AdvancedMessaging(models.Model):
    
    STATUS = Choices('draft', 'waiting', 'processed')
    
    title = models.CharField(max_length=100, blank=False)
    message_template = models.ForeignKey(MessageTemplate, blank=False)
    contact_group = models.ManyToManyField(ContactGroup)
    delivery_time = models.DateTimeField(default=get_default_time, verbose_name = "Deliver at")
       
    created_by = models.ForeignKey(KITUser, models.PROTECT)
    
    status = StatusField()
    #waiting_at = MonitorField(monitor='status', when=['waiting'])
    #processed_at = MonitorField(monitor='status', when=['processed'])
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
            
    def get_absolute_url(self):
        return reverse('messaging:advanced-message-draft',args=[self.pk])
    
    class Meta:
        verbose_name_plural = "Advanced Messaging"
    

class QueuedMessages(models.Model):
    
    MSG_TYPE = (
        ('ADVANCED',' Advanced'),
        ('STANDARD',' Standard')
                )
    
    message_type = models.CharField(max_length=10, choices=MSG_TYPE)
    message_id = models.PositiveIntegerField()   
    message = JSONField() #message, recipients
    delivery_time = models.DateTimeField(default=get_default_time, verbose_name = "Deliver at")
    
    created_by = models.ForeignKey(KITUser, models.PROTECT)
    queued_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "{} Message {}".format(self.message_type,self.message_id)
    
    def get_absolute_url(self):
        return None
    
    class Meta:
        verbose_name_plural = "Queued Messages"


class ProcessedMessages(models.Model):
    
    MSG_TYPE = (
        ('ADVANCED',' Advanced'),
        ('STANDARD',' Standard')
                )
    
    message_type = models.CharField(max_length=10, choices=MSG_TYPE)
    message = JSONField() #template, recipient_ids

    created_by = models.ForeignKey(KITUser, models.PROTECT)
    processed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "{} by {}".format(self.message_type, self.created_by)
    
    def get_absolute_url(self):
        return None
    
    class Meta:
        verbose_name_plural = "Processed Messages"
        
        
class SMSReport(models.Model):
    
    STATUS = (
        (0,'Delivered'),
        (1,'Accepted'),
        (2,'Expired'),
        (3,'Undelivered'),
        (4,'Rejected'),
              )
    
    to_phone = PhoneNumberField(blank=False)
    sms_message = JSONField() #body, messageid, 
    sms_gateway = JSONField()
    status = StatusField()
    
    owner = models.ForeignKey(KITUser, models.PROTECT)
    last_modified = models.DateTimeField(auto_now=True)
    
    #datetime sms was sent,which may be different from when it entered the processing queue
    created = models.DateTimeField(auto_now_add=True)  
    
    def __str__(self):
        return "SMS from to {}".format(self.to_phone)
    
    
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
    
    owner = models.ForeignKey(KITUser, models.PROTECT)
    last_modified = models.DateTimeField(auto_now=True)
    
    #datetime email was sent,which may be different from when it entered the processing queue
    created = models.DateTimeField(auto_now_add=True)  
    
    
    def __str__(self):
        return "Email from {} to {}".format(self.from_email,self.to_email)