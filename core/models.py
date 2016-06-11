import sys
import datetime

from django.db import models, transaction

from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from fernet_fields import EncryptedCharField
from randomslugfield import RandomSlugField
# Create your modelx here.

from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.core.exceptions import ValidationError
from django.http import request
from django.dispatch.dispatcher import receiver
from django.conf import settings




### Managers
class ActiveManager(models.Manager):
    
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(active=True)

    
class KITUserManager(models.Manager):
    
    def get_contacts(self):
        return    

def get_default_user_group():
    
    data = {
        'title':'Default',
        'description':'Default User Group',
        'kit_admin': 'self',
        'active': True,
    }
            
    return CoUserGroup.objects.get_or_create(**data)

def create_and_set_default_user_group(sender, instance, *args, **kwargs):
    
    if instance.is_admin:
        
        #if not CoUserGroup.objects.filter(title='Default', kit_admin=instance).exists():
        
        kitadmin = KITUser.objects.get(pk=instance.id)
        
        try:
            coug, created = CoUserGroup.objects.get_or_create(
                    title = 'Default',
                    description = 'Default User Group',
                    kit_admin = kitadmin,
                    defaults = {
                        'active' : True
                                }
                )
            if created:
                instance.user_group = coug
        except:
            print("Error:", sys.exc_info())


class KITUser(models.Model):
    
    INDUSTRY = (
        ('AVIATION','Aviation'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('RELIGIOUS','Religious'),
        ('FINBANK','Finance & Banking'),
        ('OTHER','Other')
    )
    
    STATE = (
        ('OYO','Oyo'),
        ('ABIA','Abia'),
        ('LAG','Lagos'),
        ('ABJ','Abuja'),
        ('ONDO','Ondo'),
        ('KANO','Kano'),
             )
    
    user = models.OneToOneField(User)
    dob = models.DateField(blank=False)
    
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'is_admin':True})
    phone_number = PhoneNumberField(blank=True, null=True, unique=True)
    company = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY, blank=False)
    address_1 = models.CharField(max_length=100, blank=False)
    address_2 = models.CharField(max_length=100, blank=True)
    city_town = models.CharField(max_length=100, blank=False)
    state = models.CharField(max_length=100, blank=False, choices=STATE, default="LAG")
    is_admin = models.BooleanField(default=False)
    
    objects = KITUserManager()
    
    def __str__(self):
        if self.user.first_name: return self.user.first_name
        else: return self.user.username
        
    def get_absolute_url(self):
        return reverse('core:kituser-detail',args=[self.pk])
        
    def get_parent(self):
        if self.is_admin:
            return False
        return self.parent
    
    def get_contacts(self):
        if self.is_admin:
            #return self.kituser_set.contact_set
            return Contact.objects.filter(kit_user__parent=self.pk)
        else:
            my_groups = self.groups_belongto.all()
            users_who_are_in_groups_i_belong_to = KITUser.objects.filter(groups_belongto__in=my_groups)
            contacts1 = Contact.objects.filter(kit_user__in=users_who_are_in_groups_i_belong_to)
            #Contact.objects.filter(kit_user__cousergroup)
            contacts2 = Contact.objects.filter(kit_user__groups_belongto__kit_admin=self.parent).distinct()
            #return {'contact1': contacts1, 'contact2':contacts2} #self.contact_set.all(cousergroup__kit_user=self.pk)
            return contacts2
            
            
    def get_private_events(self):
        if self.is_admin:
            '''
            Return the private events of all contacts created by users
            under the groups I admin over
            '''
            
            return Event.objects.filter(contact__kit_user__parent=self.pk).order_by("date")
        else:
            return Event.objects.filter(contact__kit_user__groups_belongsto__kit_admin=self.parent).order_by("date")
        
    def get_public_events(self):
        if self.is_admin:
            return PublicEvent.objects.filter(kit_user__parent=self.pk).order_by("date")
        else:
            return PublicEvent.objects.filter(kit_user__groups_belongsto__kit_admin=self.parent).order_by("date")
        
    def get_templates(self):
        if self.is_admin:
            return MessageTemplate.objects.filter(kit_admin = self.pk)
        else:
            return MessageTemplate.objects.filter(cou_group__kit_users = self.pk)
        
    #####Admin Things#######
    
    def get_kituser(self):
        if self.is_admin:
            return KITUser.objects.get(parent=self.pk)
    
    def get_kitusers(self):
        '''
        Admin, get child users
        '''
        if self.is_admin:
            return KITUser.objects.filter(parent=self.pk)
        
    def get_user_groups(self):
        '''
            Only KIT_ADMINS can configure SMTP
        '''
        if self.is_admin:
            return CoUserGroup.objects.filter(kit_admin=self.pk)
        
    def get_smtp_items(self):
        if self.is_admin:
            return SMTPSetting.objects.filter(kit_admin=self.pk)
            

post_save.connect(create_and_set_default_user_group, sender=KITUser)      


def prevent_save_of_group_titled_default(sender, instance, *args, **kwargs):
    
    if (instance.title).lower() == 'default' :
        pass

          
class CoUserGroup(models.Model):
    title = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=255, blank=True)
    kit_admin = models.ForeignKey(KITUser, on_delete=models.CASCADE, related_name='groups_adminover', \
                                  blank=False, limit_choices_to={'is_admin':True})
    kit_users = models.ManyToManyField(KITUser, related_name='groups_belongto', \
                                       blank=True, limit_choices_to={'is_admin':False,'user.is_active':True})
    active = models.BooleanField() #when deactivated, 
    
    def __str__(self):
        return self.title
    
        
    def get_absolute_url(self):
        return reverse('core:usergroup-detail',args=[self.pk])
    
    def get_contact_managed_by_group(self):
        if self.active:
            return self.contact
    '''    
    def save(self, *args, **kwargs):
        #prevent save if title is default or Default
        if (self.title).lower() != 'default':
            super(CoUserGroup, self).save(*args, **kwargs)
        elif request.user.is_admin:            
            raise ValidationError('You cannot save a Group as "default"')
    '''    
    class Meta:
        verbose_name = 'User Group'
        

        

class KITAdminAccount(models.Model):
    kit_admin = models.OneToOneField(KITUser)
    sms_balance = models.DecimalField(max_digits=12, decimal_places=4)
    last_subscribed = models.DateTimeField()
    is_multicompany = models.BooleanField()
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
    
    kit_admin = models.ForeignKey(KITUser, models.CASCADE, blank=False, limit_choices_to={'is_admin':True})
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "%s - %s"%(self.description,self.smtp_server)
    
    def get_absolute_url(self):
        return reverse('core:smtp-detail',args=[self.pk])


def set_m2m_contact_usergroup(sender, instance, created, **kwargs):
    
    if created:
        transaction.on_commit(
             lambda: instance.cou_group.add(instance.kit_user.cou_group)
        )
        

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
    #slug = modelx.SlugField(max_length=100)
    active = models.BooleanField(default=True)
    
    kit_user = models.ForeignKey(KITUser, models.PROTECT) #limit to not admin i.e admin cannot create contact
    #cou_group = modelx.ManyToManyField('CoUserGroup', blank=True)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name
    
    @property
    def get_usergroup_contact_managed_by(self):
        return '{}'.format(self.kit_user.cou_group)
    
    def get_absolute_url(self):
        return reverse('core:contact-detail',
                       args=[self.slug])
        
    def all_cou_group(self):
        return ', '.join([x.title for x in self.cou_group.all()])

#post_save.connect(set_m2m_contact_usergroup, sender=Contact) 

    
class ContactGroup(models.Model):
    title = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=255, blank=True)
    contacts = models.ManyToManyField(Contact, blank=False)
    kit_user = models.ForeignKey(KITUser, models.PROTECT, blank=False)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    
    def get_absolute_url(self):
        return reverse('core:contactgroup-detail',args=[self.pk])

class MessageTemplate(models.Model):
    title = models.CharField(max_length=100)
    email_template = models.TextField(blank=True)
    sms_template = models.TextField(blank=True)
    smtp_setting = models.ForeignKey(SMTPSetting)
    
    send_sms = models.BooleanField(verbose_name="Send SMS")
    send_email = models.BooleanField(verbose_name="Send Email")
    
    cou_group = models.ForeignKey(CoUserGroup,models.SET_NULL, null=True, verbose_name="Group Availability")
    kit_admin = models.ForeignKey(KITUser, models.PROTECT, blank=True, limit_choices_to={'is_admin':True})
    
    active = models.BooleanField()
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    @property
    def get_usergroup_template_belongs_by(self):
        return '{}'.format(self.kit_admin.user_group)
    
    def get_absolute_url(self):
        return reverse('core:templates-detail',args=[self.pk])



    
class EventManager(models.Manager):
    pass
       
class Event(models.Model):
    '''
    Event attached to contact
    '''
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=True)
    date = models.DateField(blank=False)
    message = models.ForeignKey(MessageTemplate)
    title = models.CharField(max_length=100, blank=False)
    
    #created_by_group = models.ForeignKey(CoGroup,models.SET_NULL, null=True)
    #couser = models.ForeignKey(CoUser, models.SET_NULL, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    
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
    #applies_to = models.CharField(max_length=3, choices=APPLIESTO, default='ALL')
    recipients = models.ManyToManyField(Contact, blank=True)
    all_contacts = models.BooleanField(default=False)
    #event_group = models.ForeignKey(CoUserGroup,models.SET_NULL, null=True)
    kit_user = models.ForeignKey(KITUser, models.PROTECT, blank=True)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return "%s"%(self.title)
    
    @property
    def get_group(self):
        return '{}'.format(self.kit_user.user_group)
    
    def get_absolute_url(self):
        return reverse('core:public-event-detail',
                       args=[self.pk])



    
class SentMessage(models.Model):
    event = models.ForeignKey(Event)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.event


    
