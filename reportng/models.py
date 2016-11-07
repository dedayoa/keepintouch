from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.postgres.fields.jsonb import JSONField
import uuid

# Create your models here.



class SMSDeliveryReport(models.Model):
    
    STATUS = (
        ('0', 'ACCEPTED'),
        ('1', 'PENDING'),
        ('2', 'UNDELIVERABLE'),
        ('3', 'DELIVERED'),
        ('4', 'EXPIRED'),
        ('5', 'REJECTED')
              )
    
    ERROR = (
        ('0', 'OK'),
        ('1', 'HANDSET_ERROR'),
        ('2', 'USER_ERROR'),
        ('3', 'OPERATOR_ERROR')
             )

    MSG_ORIGIN = (
        ('0', 'Transactional'),
        ('1', 'Bulk SMS'),
                  )

    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_id = models.UUIDField(db_index=True, editable=False, null=True, help_text="A.K.A Process ID or Bulk ID")
    origin = models.CharField(max_length=1, choices=MSG_ORIGIN)
    
    sms_sender = models.CharField(max_length=11, blank=True, db_index=True) #report will be generated on this field
    to_phone = PhoneNumberField(blank=False, db_index=True) #report will be generated on this field
    sms_message = JSONField()
    sms_gateway = JSONField()
    
    msg_status = models.CharField(max_length=20, choices=STATUS, default='')
    msg_error = models.CharField(max_length=20, choices=ERROR, default='')
    
    kituser_id = models.IntegerField(db_index=True) #report will be generated on this field
    kitu_parent_id = models.IntegerField(db_index=True)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True) #report will be generated on this field
    
    def __str__(self):
        return "SMS to {}".format(self.to_phone.as_international)
    

class SMSDeliveryReportHistory(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message_id = models.ForeignKey(SMSDeliveryReport, on_delete=models.CASCADE)
    data = JSONField()
    
    
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.id)
    


class SMSDeliveryReportTransaction(models.Model):

    STATUS = (
        ('0', 'Unprocessed'),
        ('1', 'Processed'),
        ('2', 'Error'),
    )

    #date_generated = models.DateTimeField()
    date_received = models.DateTimeField(auto_now_add=True)
    
    body = JSONField()
    request_meta = JSONField()
    
    status = models.CharField(max_length=20, choices=STATUS, default='0')

    def __str__(self):
        return '{0}'.format(self.date_received)
    
    
class EmailDeliveryReport(models.Model):
    
    STATUS = (
        ('0', 'SENT'), #DR
        ('1', 'PROCESSED'), #this information will be visible to us only
        ('2', 'DROPPED'),
        ('3', 'DEFERRED'),
        ('4', 'DELIVERED'),
        ('5', 'BOUNCED'),
        
        #('1', 'OPENED'), #ER
        #('2', 'CLICKED'), #ER
        #('7', 'SPAM REPORT'), #ER
        #('8', 'UNSUBSCRIBE'), #does not apply. will be handled by In.Touch
             )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_id = models.UUIDField(db_index=True, editable=False, null=True, help_text="A.K.A Process ID or Bulk ID")
    
    to_email = models.EmailField()
    from_email = models.EmailField()
    
    email_message = JSONField()
    email_gateway = JSONField()
    
    msg_status = models.CharField(max_length=20, choices=STATUS, default='')
    
    kituser_id = models.IntegerField(db_index=True) #report will be generated on this field
    kitu_parent_id = models.IntegerField(db_index=True)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True) #report will be generated on this field
    
    
    def __str__(self):
        return "Email from {} to {}".format(self.from_email,self.to_email)

class EmailEventHistory(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message_id = models.ForeignKey(EmailDeliveryReport, on_delete=models.CASCADE)
    data = JSONField()
    
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.id)
    
    
    
class CallDetailReportTransaction(models.Model):

    STATUS = (
        ('0', 'Unprocessed'),
        ('1', 'Processed'),
        ('2', 'Error'),
    )

    #date_generated = models.DateTimeField()
    date_received = models.DateTimeField(auto_now_add=True)
    
    body = JSONField()
    request_meta = JSONField()
    
    status = models.CharField(max_length=4, choices=STATUS, default='0')

    def __str__(self):
        return '{0}'.format(self.date_received)