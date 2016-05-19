from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from fernet_fields import EncryptedCharField
from randomslugfield import RandomSlugField
# Create your models here.



class CoAdmin(models.Model):
    
    INDUSTRY = (
        ('AVIATION','Aviation'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('RELIGIOUS','Religious'),
        ('FINBANK','Finance & Banking'),
        ('OTHER','Other')
                )
    
    user = models.OneToOneField(User)
    phone_number = PhoneNumberField(blank=True, unique=True)
    company = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY, blank=False)
    address_1 = models.CharField(max_length=100, blank=False)
    address_2 = models.CharField(max_length=100, blank=True)
    city_town = models.CharField(max_length=100, blank=False)
    state = models.CharField(max_length=100, blank=False)
    dob = models.DateField(blank=False)
    

    
    def __str__(self):
        if self.user.first_name: return self.user.first_name
        else: return self.user.username

class CoAccount(models.Model):
    user = models.OneToOneField(CoAdmin) 
    sms_balance = models.DecimalField(max_digits=12, decimal_places=4)
    last_subscribed = models.DateTimeField()
    subscription_expires = models.DateField()
    
class CoGroup(models.Model):
    title = models.CharField(max_length=100, blank=False)
    
    def __str__(self):
        return self.title
    
class CoUser(models.Model):
    user = models.OneToOneField(User)
    parent = models.OneToOneField(CoAdmin)
    phone_number = PhoneNumberField(blank=True)
    group = models.ManyToManyField(CoGroup)
    dob = models.DateField(blank=False)

    
    
    def __str__(self):
        if self.user.first_name: return self.user.first_name
        else: return self.user.username
    
    class Meta:
        pass

    
class SMTPSetting(models.Model):
    
    CONSEC = (
        ('NO', 'None'),
        ('STARTTLS', 'STARTTLS'),
        ('SSLTLS','SSL/TLS')
              )
    
    description = models.CharField(max_length=100, blank=True)
    smtp_server = models.CharField(max_length=255, blank=False)
    smtp_port = models.PositiveSmallIntegerField(blank=False)
    connection_security = models.CharField(max_length=20, choices=CONSEC, default='NO', blank=False)
    smtp_user = models.CharField(max_length=255, blank=True)
    smtp_password = EncryptedCharField(max_length=255,blank=True)
    
    owner = models.ForeignKey(CoGroup) #those in this group
    
    def __str__(self):
        return "%s - %s"%(self.description,self.smtp_server)

class Contact(models.Model):
    #slug = RandomSlugField(length=7, exclude_lower=True, primary_key=True)
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = PhoneNumberField(blank=True)
    #slug = models.SlugField(max_length=100)
    
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name

class EventType(models.Model):
    '''
    Type of Event with the corresponding template
    '''
    PRIVPUB = (
        ('PRI','Private'),
        ('PUB','Public'),
               )
    title = models.CharField(max_length=100)
    scope = models.CharField(max_length=3, choices=PRIVPUB, blank=False)
    email_template = models.TextField(blank=True)
    sms_template = models.TextField(blank=True)
    
    def __str__(self):
        return self.title

    
class Event(models.Model):
    '''
    Event attached to contact
    '''
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=True)
    date = models.DateField(blank=False)
    event_type = models.ForeignKey(EventType)
    smtp_setting = models.ForeignKey(SMTPSetting)
    send_sms = models.BooleanField()
    
    created_by = models.ForeignKey(User,models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "%s - %s"%(self.contact.first_name, self.event_type)   
    
class SentMessage(models.Model):
    event = models.ForeignKey(Event)
    
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.event
    
    

    
    