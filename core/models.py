import sys
import datetime
import uuid

from django.db import models, transaction
from cities_light.models import Country, Region, City

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

from timezone_utils.fields import TimeZoneField
from timezone_utils.choices import PRETTY_ALL_TIMEZONES_CHOICES, PRETTY_COMMON_TIMEZONES_CHOICES

#from messaging.models import ProcessedMessages, QueuedMessages

from django.apps import apps
from cacheops.query import cached_as
from cryptography.fernet import InvalidToken


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

class ValidatedUserAccountManager(models.Manager):
    
    @cached_as(timeout=3600) 
    def get_queryset(self):
        return super(ValidatedUserAccountManager, self).get_queryset().filter(email_validated=True, phone_validated=True)


class OrganizationContact(models.Model):
    
    INDUSTRY = (
        ('AVIATION','Aviation'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('RELIGIOUS','Religious'),
        ('FIN_BANK','Finance & Banking'),
        ('EDUCATION','Education'),
        ('MARKETING','Marketing'),
        ('GOVERNMENT','Government'),
        ('OIL_ENERGY','Oil & Energy'),
        ('NGO','NGO'),
        ('IT','Information Technology'),
        ('RETAIL','Retail'),
        ('TRANSPORT_HAULAGE','Transportation & Haulage'),
        ('TRAVEL_TOURISM','Travel & Tourism'),
        ('OTHER','Other')
    )
    
    organization = models.CharField(max_length=255, null=True, verbose_name="Organization Name")
    industry = models.CharField(max_length=50, choices=INDUSTRY, null=True)
    
    organization_phone_number = PhoneNumberField(blank=True, null=True)
    # on save use the address of the parent if this is not filled
    address_1 = models.CharField(max_length=100, blank=False, null=True)
    address_2 = models.CharField(max_length=100, blank=True, null=True)
    
    country = models.ForeignKey(Country,on_delete=models.PROTECT, blank=False)
    state = models.ForeignKey(Region,on_delete=models.PROTECT, blank=False)
    city_town = models.ForeignKey(City,on_delete=models.PROTECT, blank=False, verbose_name="City/Town")
    
    
    def __str__(self):
        return "{}, {}".format(self.address_1, self.city_town)
    
    class Meta:
        verbose_name = "Organization's Contact Detail"
    
class KITUser(models.Model):
    
    user = models.OneToOneField(User)
    dob = models.DateField(blank=False, null=True)
    timezone = TimeZoneField(choices=PRETTY_COMMON_TIMEZONES_CHOICES, null=True)
    
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'is_admin':True})
    phone_number = PhoneNumberField(blank=True, null=True)
    
    is_admin = models.BooleanField(default=False)
    address = models.OneToOneField(OrganizationContact, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, editable=False)
    
    email_validated = models.BooleanField(default=False)
    email_validated_date = models.DateTimeField(null=True)
    
    phone_validated = models.BooleanField(default=False)
    phone_validated_date = models.DateTimeField(null=True)
    
    
    objects = models.Manager()
    
    def __str__(self):
        return "{}".format(self.user.get_full_name())
        
    def get_absolute_url(self):
        return reverse('core:kituser-detail',args=[self.pk])
    
    #@cached_as(timeout=3600)    
    def get_parent(self):
        if self.is_admin:
            return self
        return self.parent
    
    def get_contacts(self):
        
        #if self.kitbilling.is_full_admin == False:
        #    return Contact.objects.filter(kit_user=self.pk)
        if self.is_admin:
            #return self.kituser_set.contact_set
            return Contact.objects.filter(kit_user__parent=self.pk)
        else:
            my_groups = self.groups_belongto.all()
            users_who_are_in_groups_i_belong_to = KITUser.objects.filter(groups_belongto__in=my_groups)
            contacts1 = Contact.objects.filter(kit_user__in=users_who_are_in_groups_i_belong_to)
            #Contact.objects.filter(kit_user__cousergroup)
            
            if self.parent.kitsystem.company_wide_contacts == True:
            
                contacts2 = Contact.objects.filter(kit_user__parent=self.parent).distinct()
            else:
                contacts2 = Contact.objects.filter(kit_user__groups_belongto__kit_admin=self.parent).distinct()
            #return {'contact1': contacts1, 'contact2':contacts2} #self.contact_set.all(cousergroup__kit_user=self.pk)
            return contacts2
        
    def get_contact_groups(self):
        if self.is_admin:
            return ContactGroup.objects.filter(kit_user=self.pk)
        else:
            return ContactGroup.objects.filter(kit_user=self.pk)
            
            
    def get_private_events(self):
                
        #if self.kitbilling.is_full_admin == False:
        #    return Event.objects.filter(contact__kit_user=self.pk)
        if self.is_admin:
            '''
            Return the private events of all contacts created by users
            under the groups I admin over
            '''
            return Event.objects.filter(contact__kit_user__parent=self.pk)
        else:
            #get events of groups I belong to
            #if you are allowed to see all contacts in the organisation,
            #then you can view the anniversaries of all of them
            if self.parent.kitsystem.company_wide_contacts == True:
                return Event.objects.filter(contact__kit_user__parent=self.parent).distinct()
            else:
                return Event.objects.filter(contact__kit_user__groups_belongto__kit_admin=self.parent).distinct()
        
    def get_public_events(self):
        
        #if self.kitbilling.is_full_admin == False:
        #    return PublicEvent.objects.filter(kit_user=self.pk).order_by("date")
        if self.is_admin:
            return PublicEvent.objects.filter(kit_user__parent=self.pk).order_by("date")
        else:
            #get events of groups I belong to. May chance this later
            if self.parent.kitsystem.company_wide_contacts == True:
                return PublicEvent.objects.filter(kit_user__parent=self.parent).order_by("date")
            else:
                return PublicEvent.objects.filter(kit_user__groups_belongto__kit_admin=self.parent).order_by("date").distinct()
        
    def get_templates(self):
        
        if self.is_admin:
            return MessageTemplate.objects.filter(kit_admin = self)
        else:
            if self.parent.kitsystem.company_wide_contacts == True:
                # get all smtp settings created by the admin
                return MessageTemplate.objects.filter(kit_admin = self.parent)
            else:
                # get smtp settings of groups I belong to.
                gib2 = self.groups_belongto.all()
                return MessageTemplate.objects.filter(cou_group__in = gib2)
        
    def get_processed_messages(self):
        processedmessages = apps.get_model('messaging', 'ProcessedMessages')
        
        #if self.kitbilling.is_full_admin == False:
        #    return processedmessages.objects.filter(created_by = self.pk)
        if self.is_admin:
            return processedmessages.objects.filter(created_by__parent = self.pk).order_by('-processed_at')
        else:
            return processedmessages.objects.filter(created_by = self.pk).order_by('-processed_at')
                
    def get_queued_messages(self):
        queuedmessages = apps.get_model('messaging', 'QueuedMessages')
        
        #if self.kitbilling.is_full_admin == False:
        #    return queuedmessages.objects.filter(created_by = self.pk).order_by('-queued_at')
        if self.is_admin:
            return queuedmessages.objects.filter(created_by__parent = self.pk).order_by('-queued_at')
        else:
            return queuedmessages.objects.filter(created_by = self.pk).order_by('-queued_at')
        
    def get_running_messages(self):
        RunningMessage = apps.get_model('messaging', 'RunningMessage')
        
        #if self.kitbilling.is_full_admin == False:
        #    return RunningMessage.objects.filter(created_by = self.pk).order_by('-started_at')
        if self.is_admin:
            return RunningMessage.objects.filter(created_by__parent = self.pk).order_by('-started_at')
        else:
            return RunningMessage.objects.filter(created_by = self.pk).order_by('-started_at')
        
        
    def get_custom_data(self):
        if self.is_admin:
            return CustomData.objects.filter(created_by__parent = self.pk)
        else:
            return CustomData.objects.filter(created_by = self.pk)
        
        
    def get_failed_email_messages(self):
        failedemailmessage = apps.get_model('messaging', 'FailedEmailMessage')
        if self.is_admin:
            return failedemailmessage.objects.filter(owned_by__parent = self.pk)
        else:
            return failedemailmessage.objects.filter(owned_by = self.pk).order_by('-created')
        
        
    def get_failed_sms_messages(self):
        failedsmsmessage = apps.get_model('messaging', 'FailedSMSMessage')
        if self.is_admin:
            return failedsmsmessage.objects.filter(owned_by__parent = self.pk)
        else:
            return failedsmsmessage.objects.filter(owned_by = self.pk).order_by('-created')
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
        #elif not self.kitbilling.is_full_admin:
        #    raise PermissionError("You don't have the necessary Permissions")
        
    def get_user_groups(self):        
        #if self.kitbilling.is_full_admin == False:
        #    raise PermissionError("You don't have the necessary Permissions")
        if self.is_admin:
            return CoUserGroup.objects.filter(kit_admin=self.pk)
        
    def get_smtp_items(self):
        '''
            Only KIT_ADMINS can configure SMTP
        '''
        try:
            if self.is_admin:
                return SMTPSetting.objects.filter(kit_admin=self.pk)
            else:
                if self.parent.kitsystem.company_wide_contacts == True:
                    # get all smtp settings created by the admin
                    return SMTPSetting.objects.filter(kit_admin = self.parent)
                else:
                    # get smtp settings of groups I belong to.
                    gib2 = self.groups_belongto.all()
                    return SMTPSetting.objects.filter(cou_group__in = gib2)
        except InvalidToken:
            print("Seems you have changed SECRET_KEY...all encrypted tokens have been invalidated")


def prevent_save_of_group_titled_default(sender, instance, *args, **kwargs):
    
    if (instance.title).lower() == 'default' :
        pass

def get_random_integers():
    import random
    n = random.randint(10000,99999)
    return n

class KITActivationCode(models.Model):
    
    user = models.OneToOneField(User)
    email_activation_code = RandomSlugField(length=28, db_index=True)
    phone_activation_code = models.CharField(max_length=5, default=get_random_integers, editable=False, db_index=True)
    
    expired = models.BooleanField(default=False)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "{}".format(self.user)
    


class KITUBalance(models.Model):
    
    kit_user = models.OneToOneField('core.KITUser')
    sms_balance = models.PositiveIntegerField(default=0)
    free_sms_balance = models.PositiveIntegerField(default=0)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "{}".format(self.kit_user)
    
    class Meta:
        verbose_name = "User Balance"

         
class CoUserGroup(models.Model):
        
    
    title = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=255, blank=True)
    kit_admin = models.ForeignKey('core.KITUser', on_delete=models.CASCADE, related_name='groups_adminover', \
                                  blank=False, limit_choices_to={'is_admin':True})
    kit_users = models.ManyToManyField('core.KITUser', related_name='groups_belongto', \
                                       blank=True, limit_choices_to={'is_admin':False})
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

    

class SMTPSetting(models.Model):
    
    CONSEC = (
        ('NO', 'None'),
        ('STARTTLS', 'STARTTLS'),
        ('SSLTLS','SSL/TLS')
              )
    
    description = models.CharField(max_length=100, blank=False)
    from_user = models.CharField(max_length=100, blank=True)
    smtp_server = models.CharField(max_length=255, blank=False)
    smtp_port = models.PositiveSmallIntegerField(blank=False)
    connection_security = models.CharField(max_length=20, choices=CONSEC, default='NO', blank=False)
    smtp_user = models.CharField(max_length=255, blank=True)
    smtp_password = EncryptedCharField(max_length=255,blank=True)
    active = models.BooleanField()
    
    kit_admin = models.ForeignKey('core.KITUser', models.CASCADE, blank=False, limit_choices_to={'is_admin':True})
    cou_group = models.ManyToManyField(CoUserGroup, verbose_name="Group Availability", blank=True)
    
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
    domain_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    #uprofile = JSONField() 
    #slug = modelx.SlugField(max_length=100)
    active = models.BooleanField(default=True)
    
    kit_user = models.ForeignKey('core.KITUser', models.PROTECT) #limit to not admin i.e admin cannot create contact
    #cou_group = modelx.ManyToManyField('CoUserGroup', blank=True)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)
    
    @property
    def get_usergroup_contact_managed_by(self):
        return '{}'.format(self.kit_user.cou_group)
    
    def get_absolute_url(self):
        return reverse('core:contact-detail',
                       args=[self.slug])
        
    def all_cou_group(self):
        return ', '.join([x.title for x in self.cou_group.all()])
    
    def cdata(self, cud):
        # con.cdata("dkkwb:our_food")
        customdata = apps.get_model('gomez', 'CustomData')
        g = cud.split(":")
        try:
            h = customdata.objects.get(pk=g[0])#self.customdata_set.get(pk = g[0])
            if h.system_id_field == "coid":
                result = h.data[self.pk][g[1]]
            elif h.system_id_field == "doid":
                result = h.data[self.domain_id][g[1]]
            return result
        except KeyError:
            #log error
            print("Seems you are using the wrong system Identity Field or it simply does not exist")
    
    #{% cdata 'x9v7a:account_id' %}
    #{{ cdata:x9v7a.account_id }}
    #{{ x9v7a:account_id }}
    #{{x9v7a|cdata:account_id}}
    # {{cdata("x9v7a:account_id")}}
#post_save.connect(set_m2m_contact_usergroup, sender=Contact) 

    
class ContactGroup(models.Model):
    title = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=255, blank=True)
    contacts = models.ManyToManyField('core.Contact', blank=False)
    kit_user = models.ForeignKey('core.KITUser', models.PROTECT, blank=False)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    
    def get_absolute_url(self):
        return reverse('core:contactgroup-detail',args=[self.pk])
    
    class Meta:
        verbose_name = 'Contact List'

class MessageTemplate(models.Model):
    title = models.CharField(max_length=100)
    email_template = models.TextField(blank=True)
    sms_template = models.TextField(blank=True)
    
    sms_sender = models.CharField(max_length=11, blank=True)
    smtp_setting = models.ForeignKey('core.SMTPSetting', models.SET_NULL, null=True, \
                                     blank=True, verbose_name="SMTP Account")
    
    send_sms = models.BooleanField(verbose_name="Send SMS")
    insert_optout = models.BooleanField(verbose_name = "Insert Unsubscribe")
    
    send_email = models.BooleanField(verbose_name="Send Email")
    
    cou_group = models.ForeignKey('core.CoUserGroup', models.SET_NULL, null=True, verbose_name="Group Availability")
    kit_admin = models.ForeignKey('core.KITUser', models.PROTECT, blank=True, limit_choices_to={'is_admin':True})
    
    active = models.BooleanField(default=True)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    
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
    contact = models.ForeignKey('core.Contact', on_delete=models.CASCADE, blank=True)
    date = models.DateField(blank=False)
    message = models.ForeignKey('core.MessageTemplate')
    title = models.CharField(max_length=100, blank=False)
    
    #created_by_group = models.ForeignKey(CoGroup,models.SET_NULL, null=True)
    #couser = models.ForeignKey(CoUser, models.SET_NULL, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    last_run = models.DateField(blank=True, default=timezone.now) #date message based on event was last sent

    
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
    message = models.ForeignKey('core.MessageTemplate')
    #applies_to = models.CharField(max_length=3, choices=APPLIESTO, default='ALL')
    recipients = models.ManyToManyField('core.Contact', blank=True)
    all_contacts = models.BooleanField(default=False)
    #event_group = models.ForeignKey(CoUserGroup,models.SET_NULL, null=True)
    kit_user = models.ForeignKey('core.KITUser', models.PROTECT, blank=True)
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return "%s"%(self.title)
    
    @property
    def get_group(self):
        return '{}'.format(self.kit_user.user_group)
    
    def get_recipients(self):
        #get contacts that belong to the group to which this user belongs
        if self.all_contacts == True:
            return self.kit_user.get_contacts()
        else:
            return self.recipients.all()
    
    
    def get_absolute_url(self):
        return reverse('core:public-event-detail',
                       args=[self.pk])



    
class SentMessage(models.Model):
    event = models.ForeignKey('core.Event')
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.event



class SMSTransfer(models.Model):
    
    from_user = models.ForeignKey('core.KITUser', models.SET_NULL, null=True, blank=False, related_name='from_user')
    to_user = models.ForeignKey('core.KITUser', models.SET_NULL, null=True, blank=False, related_name = 'to_user')
    sms_units = models.PositiveIntegerField(blank=False)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_detail = JSONField(blank=False) #in case the user is deleted
    
    created_by = models.ForeignKey('core.KITUser', models.PROTECT, blank=False, limit_choices_to={'is_admin':True})
    
    def __str__(self):
        return "{} units(s) from {} to {}".format(self.sms_units, self.from_user, self.to_user)


class UploadedContact(models.Model):
    
    name = models.CharField(max_length=30)
    #file = models.FileField(upload_to='uploaded_contact_files/%Y/%m/')
    file_json = JSONField()
    file_extension = models.CharField(max_length=4, blank=False)
    import_status = JSONField()
    upload_date = models.DateTimeField(auto_now_add=True)
    
    uploaded_by = models.ForeignKey('core.KITUser', models.CASCADE, blank=False)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('core:download-contact-file',
                       args=[self.pk])


class CustomData(models.Model):
    
    IDFLD_TYPE = (
        ('coid','Contact ID'),
        ('doid','Domain ID')
                  )
    
    namespace = RandomSlugField(length=6, exclude_vowels=True, primary_key=True)
    system_id_field = models.CharField(max_length=4, choices=IDFLD_TYPE)
    identity_column_name = models.CharField(max_length=255)
    headers = JSONField()
    data = JSONField()
    data_table = JSONField()
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.KITUser', on_delete=models.PROTECT)
    
    def __str__(self):
        return "{}".format(self.namespace)

    def get_absolute_url(self):
        return reverse('core:custom-data-ajax',args=[self.pk])