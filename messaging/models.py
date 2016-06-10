import datetime
import html2text

from django.db import models
from django.conf import settings
from django.utils import timezone


from core.models import KITUser, Contact, SMTPSetting, ContactGroup, MessageTemplate

from model_utils.fields import StatusField, MonitorField
from model_utils import Choices
from django.core.urlresolvers import reverse


def get_default_time():
    return timezone.now()+datetime.timedelta(seconds=settings.MSG_WAIT_TIME)

class StandardMessaging(models.Model):
    
    STATUS = Choices('draft', 'waiting', 'processed')
    
    email_message = models.TextField(blank=True)
    sms_message = models.TextField(blank=True)
    send_sms = models.BooleanField(verbose_name="Send SMS")
    send_email = models.BooleanField(verbose_name="Send Email")
    recipients = models.ManyToManyField(Contact)
    
    created_by = models.ForeignKey(KITUser, models.PROTECT)
    smtp_setting = models.ForeignKey(SMTPSetting, null=True, blank=True)
    sms_sender = models.CharField(max_length=11, blank=True)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    status = StatusField()
    waiting_at = MonitorField(monitor='status', when=['waiting'])
    
    
    delivery_time = models.DateTimeField(default=get_default_time, verbose_name = "Deliver at")

    def __str__(self):
        if self.send_sms:
            return "{}...".format(self.sms_message[0:25])
        elif self.send_email:
            return "{}...".format(html2text.html2text(self.email_message)[0:35])
            
            
    
    def get_absolute_url(self):
        return reverse('messaging:standard-message-draft',args=[self.pk]) 
    
    
class AdvancedMessaging(models.Model):
    
    STATUS = Choices('draft', 'waiting', 'processed')
    
    message = models.ForeignKey(MessageTemplate)    
    contact_group = models.ManyToManyField(ContactGroup)
    delivery_time = models.DateTimeField(default=(timezone.now()+datetime.timedelta(seconds=settings.MSG_WAIT_TIME)),\
                                         verbose_name = "Deliver at")
    
    created_by = models.ForeignKey(KITUser, models.PROTECT)
    
    status = StatusField()
    draft_at = MonitorField(monitor='status', when=['draft'])
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)