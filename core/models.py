from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from fernet_fields import EncryptedCharField
# Create your models here.

class CoAdmin(models.Model):
    
    INDUSTRY = (
        ('AVIATION','Aviation'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('RELIGIOUS','Religious'),
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


    
class CoGroup(models.Model):
    title = models.CharField(max_length=100, blank=False)
    
    def __str__(self):
        return self.title
    
class CoUser(models.Model):
    user = models.OneToOneField(User)
    admin = models.OneToOneField(CoAdmin)
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
    
    def __str__(self):
        return "%s - %s"%(self.description,self.smtp_server)
    

    
class ContactList(models.Model):
    name = models.CharField(max_length=100, blank=False)
    sender_name = models.CharField(max_length=244, blank=False) #sms sender or email name
    smtp_setting = models.OneToOneField(SMTPSetting)
    send_sms = models.BooleanField()
    
    created_by = models.ForeignKey(User,models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name    
      

class Contact(models.Model):
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = PhoneNumberField(blank=True)
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    contact_list = models.ForeignKey(ContactList)

    def __str__(self):
        return self.first_name
    
    
    
class Event(models.Model):
    
    PRIVPUB = (
        ('pri','Private'),
        ('pub','Public'),
               )
    
    name = models.CharField(max_length=100, blank=False)
    greeting = models.CharField(max_length=100, blank=True)
    eventclass = models.CharField(max_length=3, choices=PRIVPUB, blank=False)
    date = models.DateField(blank=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=True)
    
    def __str__(self):
        return "%s - %s"%(self.name,self.contact.first_name)
    

    
    
class Message(models.Model):
    title = models.CharField(max_length=100, blank=False)
    email_body = models.TextField(blank=True)
    sms_body = models.TextField(blank=True)
    contacts = models.ManyToManyField(ContactList)
    
    owner = models.ForeignKey(CoAdmin)
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    

    
    