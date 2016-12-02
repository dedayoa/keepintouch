import decimal
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.postgres.fields.jsonb import JSONField
import uuid
from django_prices.models import PriceField
from django.conf import settings

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
        ('6', 'SENDING...')
        
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
    
    kituser_id = models.IntegerField(db_index=True, editable=False) #report will be generated on this field
    kitu_parent_id = models.IntegerField(db_index=True, editable=False)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True) #report will be generated on this field
    
    
    def __str__(self):
        return "Email from {} to {}".format(self.from_email,self.to_email)

class EmailEventHistory(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evtype = models.CharField(max_length=75, null=True)
    email = models.CharField(max_length=150, null=True)
    message_id = models.ForeignKey(EmailDeliveryReport, on_delete=models.CASCADE)
    evdata = JSONField()
    
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.id)
    
    
class EmailReportTransaction(models.Model):

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
    

class CallDetailReport(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    
    a_leg_billsec = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    b_leg_billsec = models.DecimalField(max_digits=12, decimal_places=4, default=0, blank=True)
    
    a_leg_callerid = models.CharField(max_length=50)
    b_leg_callerid = models.CharField(max_length=50, blank=True)
    
    a_leg_called_number = models.CharField(max_length=50)
    b_leg_called_number = models.CharField(max_length=50, blank=True)
    
    a_leg_call_start = models.DateTimeField(null=True)
    
    a_leg_uuid = models.ForeignKey('reportng.CallDetailReportTransaction', null=True, on_delete=models.SET_NULL, related_name='acdrt')
    b_leg_uuid = models.ForeignKey('reportng.CallDetailReportTransaction', null=True, on_delete=models.SET_NULL, related_name='bcdrt')
    
    
    a_leg_per_min_call_price = PriceField('A-Leg Cost', currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2, default=0)
    b_leg_per_min_call_price = PriceField('B-Leg Cost', currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2, default=0)
    
    total_call_cost = PriceField('Total Cost', currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2, null=True)
    
    kituser_id = models.IntegerField(db_index=True, editable=False) #report will be generated on this field
    kitu_parent_id = models.IntegerField(db_index=True, editable=False)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True) #report will be generated on this field
    
    
    def get_total_billable_call_duration(self):
        # return the billable seconds for both the A & B legs
        return self.a_leg_billsec+self.b_leg_billsec
    
    def get_total_call_cost(self):
        # return the total call cost. I save the per_min_call_price for historial reasons
        a_leg_tp = decimal.Decimal(self.a_leg_billsec/60)*self.a_leg_per_min_call_price
        b_leg_tp = decimal.Decimal(self.b_leg_billsec/60)*self.b_leg_per_min_call_price
        return a_leg_tp+b_leg_tp

    def save(self, *args, **kwargs):
        self.total_call_cost = self.get_total_call_cost()
        super(CallDetailReport,self).save(*args, **kwargs)
    
class CallDetailReportTransaction(models.Model):

    STATUS = (
        ('0', 'Unprocessed'),
        ('1', 'Processed'),
        ('2', 'Error'),
    )

    #date_generated = models.DateTimeField()
    date_received = models.DateTimeField(auto_now_add=True)
    
    call_uuid = models.UUIDField(primary_key=True, editable=False)
    body = JSONField()
    request_meta = JSONField()
    
    status = models.CharField(max_length=4, choices=STATUS, default='0')

    def __str__(self):
        return '{0}'.format(self.call_uuid)