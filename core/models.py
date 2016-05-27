from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from fernet_fields import EncryptedCharField
from randomslugfield import RandomSlugField
# Create your models here.

from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.utils import timezone

### Managers
class ActiveManager(models.Manager):
    
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(active=True)

    
class CoGroup(models.Model):
    title = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=255, blank=True)
    active = models.BooleanField()
    
    def __str__(self):
        return self.title
    

class CoUser(models.Model):
    
    INDUSTRY = (
        ('AVIATION','Aviation'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('RELIGIOUS','Religious'),
        ('FINBANK','Finance & Banking'),
        ('OTHER','Other')
                )
    
    user = models.OneToOneField(User)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    phone_number = PhoneNumberField(blank=True, unique=True)
    company = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY, blank=False)
    address_1 = models.CharField(max_length=100, blank=False)
    address_2 = models.CharField(max_length=100, blank=True)
    city_town = models.CharField(max_length=100, blank=False)
    state = models.CharField(max_length=100, blank=False)
    dob = models.DateField(blank=False)
    group = models.ManyToManyField(CoGroup)
    is_coadmin = models.BooleanField(default=False)

    
    def __str__(self):
        if self.user.first_name: return self.user.first_name
        else: return self.user.username

class CoAccount(models.Model):
    user = models.OneToOneField(CoUser)
    sms_balance = models.DecimalField(max_digits=12, decimal_places=4)
    last_subscribed = models.DateTimeField()
    subscription_expires = models.DateField()
    

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
    active = models.BooleanField()
    
    created_by_group = models.ForeignKey(CoGroup,models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "%s - %s"%(self.description,self.smtp_server)


class Contact(models.Model):
    
    SALUTATION = (
        ('mr','Mr'),
        ('mrs','Mrs'),
        ('ms','Ms'),
        ('chief','Chief'),
        ('dr','Dr')
                  )
    slug = RandomSlugField(length=9, exclude_lower=True, primary_key=True)
    salutation = models.CharField(max_length=10, choices=SALUTATION, blank=True)
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = PhoneNumberField(blank=True)
    #uprofile = JSONField() 
    #slug = models.SlugField(max_length=100)
    active = models.BooleanField(default=True)
    
    created_by_group = models.ForeignKey(CoGroup,models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name
    
    @property
    def group(self):
        return '{}'.format(self.created_by_group)
    
    def get_absolute_url(self):
        return reverse('core:contact-detail',
                       args=[self.slug])
        

class MessageTemplate(models.Model):
    title = models.CharField(max_length=100)
    email_template = models.TextField(blank=True)
    sms_template = models.TextField(blank=True)
    smtp_setting = models.ForeignKey(SMTPSetting)
    send_sms = models.BooleanField()
    
    created_by_group = models.ForeignKey(CoGroup,models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
       
class Event(models.Model):
    '''
    Event attached to contact
    '''
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=True)
    date = models.DateField(blank=False)
    message = models.ForeignKey(MessageTemplate)
    title = models.CharField(max_length=100, blank=False)
    
    #created_by_group = models.ForeignKey(CoGroup,models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "%s - %s"%(self.contact.first_name, self.title)
    
    #@todo
    def next_event(self):
        now = timezone.now()

    def get_absolute_url(self):
        return reverse('core:event-detail',
                       args=[self.pk])
    
    
class PublicEvent(models.Model):
    
    APPLIESTO = (
        ('ALL','All'),
        ('SEL','Select')
                 )
    
    title = models.CharField(max_length=100, blank=False)
    date = models.DateField(blank=False)
    message = models.ForeignKey(MessageTemplate)
    applies_to = models.CharField(max_length=3, choices=APPLIESTO, default='ALL')
    contacts = JSONField(blank=True)
    
    created_by_group = models.ForeignKey(CoGroup,models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "%s"%(self.title)
    
    
class SentMessage(models.Model):
    event = models.ForeignKey(Event)
    
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.event
    
