from django.db import models

# Create your models here.

from django.core.urlresolvers import reverse
from django.conf import settings

from randomslugfield.fields import RandomSlugField
from django.contrib.postgres.fields.jsonb import JSONField
from country_dialcode.models import Prefix

from django.utils.translation import ugettext_lazy as _
from model_utils.fields import StatusField, MonitorField
from model_utils import Choices

from phonenumber_field.modelfields import PhoneNumberField

from prices import Price
from satchless.item import Item, ItemLine, ItemSet
from django_prices.models import PriceField
from django.core.validators import MaxValueValidator, MinValueValidator

from core.models import KITUser, OrganizationContact
from livefield import LiveField, LiveManager
    
    
class KITServicePlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    active = models.BooleanField(default=True)
    
    free_sms = models.BooleanField(default=False, help_text="Weekly Free SMS?")
    free_sms_units = models.PositiveIntegerField(help_text="Number of Weekly Free SMS", default=0)
    
    user_accounts_allowed = models.PositiveIntegerField(default=0)
    user_groups_allowed = models.PositiveIntegerField(default=0)
    
    can_use_custom_data = models.BooleanField(default=False)
    api_access = models.BooleanField(default=False)
    
    sms_unit_bundle = models.PositiveIntegerField(default=0)
    email_unit_bundle = models.PositiveIntegerField(default=0)
    
    data_collection_capacity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
class Product(models.Model, Item):
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    meta = JSONField()
    
    price = PriceField('Price', currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2)
    active = models.BooleanField(default=True)
    
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True, null=True)
    
    
    def __str__(self):
        return self.name
    
    
    
class OrderLine(models.Model, ItemLine):
        
    ONETIME = 'OT'
    MONTHLY = 'MO'
    QUARTERLY = 'QU'
    BIANNUALLY = 'BI'
    ANNUALLY = 'AN'
    BIENNIALLY = 'BE'
    
    BILL_CY = (
        (ONETIME, 'One Time'),
        (MONTHLY, 'Monthly - 1month'),
        (QUARTERLY, 'Quarterly - 3months'),
        (BIANNUALLY, 'Biannually - 6months'),
        (ANNUALLY, 'Annually - 1year'),
        (BIENNIALLY, 'Biennially - 2years'),
               )
    
    product = models.ForeignKey(Product, blank=True, null=True, related_name='+',on_delete=models.SET_NULL)
    
    order = models.ForeignKey('gomez.Order', blank=True, null=True)
    billing_cycle = models.CharField(max_length=2, choices=BILL_CY)
    
    unit_price_net = models.DecimalField(_('Net Price'),max_digits=12, decimal_places=4)
    unit_price_gross = models.DecimalField(_('Gross Price'), max_digits=12, decimal_places=4)
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    
    def __str__(self):
        return self.product.__str__()
    
    def get_price_per_item(self, **kwargs):
        return Price(net=self.unit_price_net, gross=self.unit_price_gross, currency=settings.DEFAULT_CURRENCY)
    
    def get_quantity(self):
        return self.quantity
    
    def change_quantity(self, new_quantity):
        #order = self.delivery_group.order
        self.quantity = new_quantity
        self.save()
        
    def get_line_total(self):
        return self.get_quantity() * self.get_price_per_item()

class PaymentMethod(models.Model):
    GWTYPE = (
        ('ONLINE','Online'),
        ('BANK','Bank'),
              )
    
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    
    gateway_detail = JSONField()
    gateway_type = models.CharField(max_length=20, blank=True, choices=GWTYPE)  
    
    
    def __str__(self):
        return "{} - {}".format(self.name, self.get_gateway_type_display())
    
class Invoice(models.Model):
    
    INVOICE_STATUS = (
        ('PAID','Paid'),
        ('UNPA','Unpaid'),
        ('OVDU','Overdue'),
        ('CAND','Cancelled'),
        ('REFD','Refunded'),
        )
    
    customer = models.ForeignKey(KITUser, blank=True, null=True, limit_choices_to={'is_admin':True})
    invoice_alt = models.CharField(max_length=30, unique=True, default='') #invoice alternative id
    order = models.ForeignKey('gomez.Order', null=True, blank=True)
    
    date_raised = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    date_paid = models.DateTimeField(null=True, blank=True)
    
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    note = models.TextField()
    
    total_net = PriceField(currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,blank=True, null=True)
    total_tax = PriceField(currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,blank=True, null=True)
    
    status = models.CharField(max_length=4, choices=INVOICE_STATUS)
    
    def __str__(self):
        return 'Invoice #'.format(self.id)
    
    @property
    def total(self):
        if self.total_net is not None:
            gross = self.total_net.net + self.total_tax.gross
            return Price(net=self.total_net.net, gross=gross, currency=settings.DEFAULT_CURRENCY)

    @total.setter
    def total(self, price):
        self.total_net = price
        self.total_tax = Price(price.tax, currency=price.currency)
        
            
class Order(ItemSet, models.Model):
    PENDING = 'PE'
    ACTIVE = 'AC'
    CANCELLED = 'CA'
    FRAUD = 'FR'    
    
    ORDER_STATUS = (
        (PENDING,'Pending'),
        (ACTIVE,'Active'),
        (CANCELLED,'Cancelled'),
        (FRAUD,'Fraud'),
    )
    
    status = models.CharField('order status', max_length=32, choices=ORDER_STATUS, default=PENDING)
    order_number = RandomSlugField(length=10, exclude_lower=True, exclude_vowels=True, unique=True)
    
    ip_address = models.GenericIPAddressField(null=True, editable=False)
    
    customer = models.ForeignKey(KITUser, blank=True, null=True, limit_choices_to={'is_admin':True})
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, null=True)
    note = models.CharField(max_length=255, blank=True)
    
    total_net = PriceField(currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,blank=True, null=True)
    total_tax = PriceField(currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,blank=True, null=True)
    
    billing_address = models.ForeignKey(OrganizationContact, on_delete=models.PROTECT, blank=True, null=True)
    
    live = LiveField()
    objects = LiveManager()
    all_objects = LiveManager(include_soft_deleted=True)
    
    created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('id','order_number','live')
    
    def __iter__(self):
        if self.id:
            return iter(self.orderline_set.all())
        return super(Order, self).__iter__()
        
    def __str__(self):
        return 'Order {}'.format(self.order_number)
    
    def save(self, *args, **kwargs):
        self.billing_address = self.customer.address
        return super(Order, self).save(*args, **kwargs)
        
    
    def delete(self, using=None):
        self.live = False
        self.save(using=using)

    def get_items(self):
        #return OrderLine.objects.filter(delivery_group__order=self)
        return self.orderline_set.all()
        
    @property
    def total(self):
        if self.total_net is not None:
            gross = self.total_net.net + self.total_tax.gross
            return Price(net=self.total_net.net, gross=gross, currency=settings.DEFAULT_CURRENCY)

    @total.setter
    def total(self, price):
        self.total_net = price
        self.total_tax = Price(price.tax, currency=price.currency)
        
        
        
    def create_history_entry(self, comment='', status=None, user=None):
        if not status:
            status = self.status
        self.history.create(status=status, comment=comment, user=user)
        
    def get_absolute_url(self):
        return reverse('gomez:order-cart', args=[self.order_id])
        
        

class KITBilling(models.Model):
    
    PENDING = 'PE'
    ACTIVE = 'AC'
    SUSPENDED = 'SU' 
    TERMINATED = 'TE'
    CANCELLED = 'CA'
    FRAUD = 'FR' 
    
    ACCT_STATUS = (
        (PENDING,'Pending'),
        (ACTIVE,'Active'),
        (SUSPENDED,'Suspended'),
        (TERMINATED,'Terminated'),
        (CANCELLED,'Cancelled'),
        (FRAUD,'Fraud'),
        )

    BILL_CY = (
        ('MO', 'Monthly'),
        ('QU', 'Quarterly'),
        ('BI', 'Semi-Annually'),
        ('AN', 'Annually'),
        ('BE', 'Biennially'),
               )
    
    kit_admin = models.OneToOneField('core.KITUser', limit_choices_to={'is_admin':True})
    
    last_renew_date = models.DateField(editable=False)
    next_due_date = models.DateField()
    registered_on = models.DateField()
    
    service_plan = models.ForeignKey(KITServicePlan, blank=True, null=True)
    billing_cycle = models.CharField(max_length=2, choices=BILL_CY, default='AN')
    account_status = models.CharField(max_length=2, choices=ACCT_STATUS, default='PE')
    
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)            
    
    class Meta:
        verbose_name = 'Billing'
        
    def __str__(self):
        return "{} {}".format(self.kit_admin.user.first_name,self.kit_admin.user.last_name)
    
    

    
    
class KITSystem(models.Model):
    # SaaS user "system" model
    # Where a user can define account/system specific settings
    
    kit_admin = models.OneToOneField('core.KITUser', limit_choices_to={'is_admin':True}, null=True)
    company_wide_contacts = models.BooleanField(verbose_name="Organisation-wide Contacts",\
                                                help_text="Check if you want all users to see contacts from all groups",\
                                                default=True)
    sms_unsubscribe_message = models.TextField(max_length="300", verbose_name="SMS Opt-out Message", \
                                               default="To Stop receiving SMS from us, click",
                                               help_text = "We will automatically insert the opt-out link at the end\
                                               of this message")
    default_sms_sender = models.CharField(max_length=11, blank=True, verbose_name="Default SMS Sender",\
                                             help_text="Set a Default SMS Sender that will be Pre-filled where necessary")
    
    last_modified = models.DateTimeField(auto_now=True)
    
    did_number = models.CharField(max_length=30, blank=True, verbose_name="DID Number")
    
    #user_phone_as_callerid = models.BooleanField(default=False, verbose_name="User Phone Number as Caller ID")
    
    max_standard_message = models.PositiveIntegerField(help_text="Maximum number of Recipients Allowed for Standard Message",default=50)
    
    def __str__(self):
        return "{} {}".format(self.kit_admin.user.first_name,self.kit_admin.user.last_name)
    
    
    def get_absolute_url(self):
        return reverse('gomez:system-settings')

    
    
class SMSRateTable(models.Model):
    
    dialcode = models.OneToOneField(Prefix, verbose_name=_("Destination"), help_text=_("Select Prefix"))
    sms_cost = models.DecimalField(max_digits=12, decimal_places=4)
    
    
    def __str__(self):
        return str(self.dialcode)
    
    
class CallRateTable(models.Model):
    dialcode = models.OneToOneField(Prefix, verbose_name=_("Destination"), help_text=_("Select Prefix"))
    call_cost = models.DecimalField(max_digits=12, decimal_places=4)
    
    def __str__(self):
        return str(self.dialcode)
        
        
class SMSReport(models.Model):
    
    STATUS = Choices('delivered','accepted','expired','undelivered','rejected')
    
    to_phone = PhoneNumberField(blank=False)
    gw_msg_id = models.CharField(max_length=255, blank=True, null=True)
    sms_message = JSONField() #body, messageid,
    sms_gateway = JSONField()
    status = StatusField()
    
    owner = models.ForeignKey('core.KITUser', models.PROTECT)
    last_modified = models.DateTimeField(auto_now=True)
    
    #datetime sms was sent,which may be different from when it entered the processing queue
    created = models.DateTimeField(auto_now_add=True)  
    
    def __str__(self):
        return "SMS from {} to {}".format(self.owner, self.to_phone.as_international)
    
    
class EmailReport(models.Model):
    
    STATUS = Choices('sent','delivered','deferred','bounce')
    #(4,'Spam Report'),
    
    status = StatusField()
    to_email = models.EmailField()
    from_email = models.EmailField()
    email_message = JSONField()
    email_gateway = JSONField()
    
    owner = models.ForeignKey('core.KITUser', models.PROTECT)
    last_modified = models.DateTimeField(auto_now=True)
    
    #datetime email was sent,which may be different from when it entered the processing queue
    created = models.DateTimeField(auto_now_add=True)  
    
    
    def __str__(self):
        return "Email from {} to {}".format(self.from_email,self.to_email)