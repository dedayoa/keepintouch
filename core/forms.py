'''
Created on May 23, 2016

@author: Dayo
'''

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext
from django.views.generic.edit import ModelFormMixin
from django.forms.models import formset_factory, inlineformset_factory
from django.conf import settings


from .models import Contact, Event, PublicEvent, MessageTemplate, KITUser, SMTPSetting, ContactGroup,\
                    KITUBalance, OrganizationContact
from .helper import EventFormSetHelper


from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms_foundation.layout import ButtonGroup, ButtonHolder, Div,\
                                            Submit, Reset, Button, Layout, Fieldset, Row, Column
from django_select2.forms import Select2Widget, Select2MultipleWidget,\
    ModelSelect2MultipleWidget
from tinymce.widgets import TinyMCE
from crispy_forms.templatetags.crispy_forms_field import css_class
from core.models import CoUserGroup
from django.contrib.auth.models import User

from django.utils import timezone
import datetime
from django.template.defaultfilters import filesizeformat
from phonenumber_field.formfields import PhoneNumberField
from timezone_utils.forms import TimeZoneField
from timezone_utils.choices import PRETTY_COMMON_TIMEZONES_CHOICES

from cities_light.forms import RegionForm, CityForm, CountryForm


class ContactForm(forms.ModelForm):
    
    error_css_class = 'alerterror'
    first_name = forms.CharField(label=_('First Name'), widget=forms.TextInput(attrs={'required':''}), required=True)
    
    def __init__(self, *args, **kwargs):
        
        super(ContactForm, self).__init__(*args, **kwargs)
        #had to move the above here from below and also pass self to formhelper to get the layout.append
        #to work
        self.fields['domain_id'].label = _("Domain ID")
        self.helper = FormHelper(self)
        self.helper.attrs = {'data_abide': ''}
        #self.helper.form_method = 'post'
        self.helper.form_tag = False
        
        '''
        self.helper.layout = Layout(
            ButtonHolder(
                HTML('<a class="button alert" href="{% url \'core:contact-delete\' contactid %}">Delete</a>'),
                Reset('reset', _('Reset'), css_class="float-right"),
                Submit('submit', _('Submit'), css_class="success float-right")
            )
                                    )
        '''
        #self.helper.add_input(Button('delete', _('Delete'), css_class="alert float-left"))
        #self.helper.add_input(Submit('submit', _('Submit'), css_class="success float-right"))
        #self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
        
        #the below took me a while to figure out and might come in handy later.
        #self.helper.layout.append(HTML('<a class="button alert float-left" href="{% url \'core:contact-delete\' contactid %}">Delete</a>'))
        
        
    def clean(self):
        """
        User must enter either phone number or email. At least one must be entered
        """
        cleaned_data = super(ContactForm, self).clean()
        phone_number = cleaned_data.get("phone")
        email = cleaned_data.get("email")
        
        if not (phone_number or email):
            #msg = 'You must enter at least a phone number or an email address'
            self.add_error('phone','')
            self.add_error('email','')
            raise forms.ValidationError(
                'You must enter at least a valid phone number or an email address'
                                        )
            
    
    
    class Meta:
        model = Contact
        fields = ['salutation','first_name','last_name','email','phone','domain_id','active']
        labels = {
            #'user_group': _('User Group'),
        }


class EventForm(forms.ModelForm):
    
    date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS,\
                           widget=forms.DateInput(attrs={'data-date-format':'mm/dd/yy',\
                                                         'class':'event-form-date'}))
    
    def __init__(self, *args, **kwargs):
        
        super(EventForm, self).__init__(*args, **kwargs)        
        self.helper = FormHelper(self)        
        self.helper.attrs = {'data_abide': ''}
        
    
    class Meta:
        model = Event
        fields = ['contact','date','title','message']
        
EventFormSet = inlineformset_factory(Contact, Event, fields=('date','title','message'), form = EventForm, extra=2)        






class NewContactForm(forms.ModelForm):
    
    first_name = forms.CharField(label=_('First Name'), widget=forms.TextInput(attrs={'required':''}), required=True)
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.attrs = {'data_abide': ''}
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Submit'), css_class="success float-right"))
        self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
        super(NewContactForm, self).__init__(*args, **kwargs)
        self.fields['domain_id'].label = _("Domain ID")
    
    def clean(self):
        """
        User must enter either phone number or email. At least one must be entered
        """
        cleaned_data = super(NewContactForm, self).clean()
        phone_number = cleaned_data.get("phone")
        email = cleaned_data.get("email")
        
        if not (phone_number or email):
            #msg = 'You must enter at least a phone number or an email address'
            self.add_error('phone','')
            self.add_error('email','')
            raise forms.ValidationError(
                'You must enter at least a phone number or an email address'
                                        )
    
    class Meta:
        model = Contact
        fields = ['salutation','first_name','last_name','email','phone','domain_id','active']
        labels = {
            #'user_group': _('Group'),
        }

class PublicEventForm(forms.ModelForm):
    
    date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS,\
                           widget=forms.DateInput(attrs={'class':'event-form-date'}))
    
    def __init__(self, *args, **kwargs):
        
        super(PublicEventForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', _('Submit'), css_class="success float-right"))
        self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
        
        
    def clean(self):
        cleaned_data = super(PublicEventForm, self).clean()
        ev_date = cleaned_data.get("date")
        print(ev_date)
        
        if ev_date == None:
            raise forms.ValidationError("Date cannot be empty")
        
        elif ev_date < datetime.date.today():
            self.add_error('date','')
            raise forms.ValidationError("PublicEvent date has to be in the future")
        
    
    class Meta:
        model = PublicEvent    
        fields = ['title','date','message','all_contacts','recipients']
        widgets = {
            'recipients': Select2MultipleWidget,
            'message' : Select2Widget
        }  
        
        
class MessageTemplateForm(forms.ModelForm):
    
    #cou_group = forms.MultipleChoiceField(label=_("Group Availability"), widget=Select2Widget)
    
    def __init__(self, *args, **kwargs):
        super(MessageTemplateForm, self).__init__(*args, **kwargs)
        
        #self.fields['cou_group'].label = "Group Availability"
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', _('Submit'), css_class="success float-right"))
        self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
        
        self.helper.layout = Layout(
            Row(Column('title')),
            Row(Column('email_template'), css_class = "email-template"),
            Row(Column('sms_template')),
            HTML('''
                <div class="sms-textarea-status-bar row columns">
                    <div class="column small-4">Length: <span class="length"></span></div>
                    <div class="column small-4">Messages: <span class="messages"></span></div>
                    <div class="column small-4">Remaining: <span class="remaining"></span></div>
                </div>'''
                ),
            Row(Column('active')),                      
            Fieldset(
                 ugettext('Delivery settings'),
                 Row(Column('cou_group')),
                 Row(Column('smtp_setting')),
                 Row(
                     Column('send_sms', css_class="float-left small-6"),
                     Column('send_email', css_class="float-left small-6")
                     ),
                 Row(Column('sms_sender')),
                 css_class = "new-template-settings-fieldset"
                 ),                       
            )
    
    
    def clean(self):
        """
        User must Check either Send SMS or Send Email before sending
        """
        cleaned_data = super(MessageTemplateForm, self).clean()

        
        send_sms = cleaned_data.get("send_sms", False)
        send_email = cleaned_data.get("send_email", False)
        
        if not (send_sms or send_email):
            #msg = 'You must enter at least a phone number or an email address'
            raise forms.ValidationError(
                'You must select either "Send SMS" or "Send Email", or both.'
                                        )
        if send_sms and not bool(cleaned_data.get('sms_template')):
            raise forms.ValidationError('By checking "send sms", you must create an SMS template')
        
        if send_sms and not cleaned_data.get('sms_sender', False):
            self.add_error('sms_sender', 'SMS Sender is required')
            raise forms.ValidationError('SMS Sender ID is required to send SMS')
        
        if send_email and not bool(cleaned_data.get('email_template')):
            raise forms.ValidationError("Send Email checked, you must create an Email template")
        
        if send_email and not bool(cleaned_data.get('title')):
            raise forms.ValidationError("Send Email checked, email should have a Title/Subject")
        
        # clean delivery time
        send_at = cleaned_data.get("delivery_time")
        
        if send_at == None or send_at < timezone.now():
            #raise forms.ValidationError('Your Delivery Date Cannot be in the past')
            cleaned_data["delivery_time"] = datetime.datetime.now()

        
        return cleaned_data  
    
    
    class Meta:
        model = MessageTemplate
        fields = ['title', 'email_template', 'sms_template', 'active', 'cou_group', \
                  'smtp_setting', 'sms_sender','send_sms','send_email']        
        widgets = {
            'cou_group': Select2Widget,
            'smtp_setting' : Select2Widget,
            'email_template' : TinyMCE(attrs={'cols': 20,'rows':10}),
            'sms_template' : forms.Textarea(attrs={'rows':5})
        }


class ExistingUserForm(forms.ModelForm):
    
    username = forms.CharField(disabled=True)
    
    def __init__(self, *args, **kwargs):
        super(ExistingUserForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class="success float-right"))
        #self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
    
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','is_active']  



class PersonalProfileForm(forms.ModelForm):
    
    username = forms.CharField(disabled=True)
    
    def __init__(self, *args, **kwargs):
        super(PersonalProfileForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class="success float-right"))
        #self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
    
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name',]


class NewUserForm(forms.ModelForm):
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    
    def __init__(self, *args, **kwargs):
        
        self.kuser = kwargs.pop('kituser') or None
        
        super(NewUserForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_tag = False
        
    def clean(self):
        if self.kuser.get_kitusers().count() >= self.kuser.kitbilling.service_plan.user_accounts_allowed:
            raise forms.ValidationError("Your plan allows a maximum of {} Users. Consider Upgrading".\
                                        format(self.kuser.kitbilling.service_plan.user_accounts_allowed)) 
    
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name',\
                  'is_active'
                  ]       
        
class KITUserForm(forms.ModelForm):
    
    dob = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS,\
                           widget=forms.DateInput(attrs={'class':'dob-form-date'}))
    
    
    def __init__(self, *args, **kwargs):
        super(KITUserForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class="success float-right"))
        #self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
    
    class Meta:
        model = KITUser
        fields = ['timezone','dob','phone_number']
        exclude = ['user']
        widgets = {
            'timezone': Select2Widget,
                   }



class KITUBalanceForm(forms.ModelForm):

    sms_balance = forms.IntegerField(disabled=True, required=False, label="SMS Balance")
    
    def __init__(self, *args, **kwargs):
        super(KITUBalanceForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = ''
        self.helper.form_tag = False
    
    class Meta:
        model = KITUBalance
        fields = ['sms_balance']
       
        
class SMTPSettingForm(forms.ModelForm):
    
    
    smtp_password = forms.CharField(widget=forms.PasswordInput(render_value=True))
    
    def __init__(self, *args, **kwargs):
        super(SMTPSettingForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', _('Save'), css_class="success float-right"))
        self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
        #self.helper.add_input(Button('test_smtp_server', _('Test Server'), css_class="warning float-right test-smtp-button"))
    
    class Meta:
        model = SMTPSetting
        fields = [
                  'description','from_user','smtp_server','smtp_port','connection_security',\
                  'smtp_user','smtp_password', 'active'
                  ]
        
class UserGroupSettingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        
        self.kuser = kwargs.pop('kituser') or None
        
        super(UserGroupSettingForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', _('Save'), css_class="success float-right"))
        self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
        self.fields['kit_users'].queryset = self.fields['kit_users'].queryset.filter(parent=self.kuser)
        
        
    def clean(self):
        if self.kuser.get_user_groups().count() >= self.kuser.kitbilling.service_plan.user_groups_allowed:
            raise forms.ValidationError("Your plan allows a maximum of {} User Groups. Consider Upgrading".\
                                        format(self.kuser.kitbilling.service_plan.user_groups_allowed)) 
    
    class Meta:
        model = CoUserGroup
        fields = ['title','description','active','kit_users']
        widgets = {
            'kit_users' : Select2MultipleWidget,
                   }
        labels = {'kit_users' : _('Users')}
        
        
class ContactGroupForm(forms.ModelForm):
    
    title = forms.CharField(label=_('Title'), widget=forms.TextInput(attrs={'required':''}), required=True)

    def __init__(self, *args, **kwargs):
        self.kuser = kwargs.pop('kituser') or None
        
        super(ContactGroupForm, self).__init__(*args, **kwargs)
        
        self.fields['contacts'].queryset = self.kuser.get_contacts()
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', _('Submit'), css_class="success float-right"))
        self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
    
    class Meta:
        model = ContactGroup
        fields = ['title','description','contacts']
    
        widgets = {
            'contacts' : Select2MultipleWidget,
                   }

class SMSTransferForm(forms.Form):
    
    users = forms.ModelChoiceField(queryset=None, empty_label='-- Select A User --', widget=Select2Widget)
    admin = forms.CharField(widget=None)#(widget=forms.HiddenInput(attrs={'value':'{{adminid}}'}))
    amount = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'min':settings.MIN_SMS_TRANSFERABLE, 'pattern':"^[0-9]"}))
    
    def __init__(self, *args, **kwargs):
        self.crequest = kwargs.pop('crequest') or None
        super(SMSTransferForm, self).__init__(*args, **kwargs)        
        self.fields['users'].queryset = self.crequest.user.kituser.get_kitusers()
        self.fields['admin'].widget = forms.HiddenInput(attrs={'value':self.crequest.user.kituser.id})
        
        
    def clean(self):
        
        cleaned_data = super(SMSTransferForm, self).clean()
        
        
        if cleaned_data.get("amount",0) < settings.MIN_SMS_TRANSFERABLE:
            raise forms.ValidationError("Amount needs to be at least {}".format(settings.MIN_SMS_TRANSFERABLE));
        
        if cleaned_data.get("users") is None:
            raise forms.ValidationError("You must select a user")



class ContactImportForm(forms.Form):
    
    name = forms.CharField(max_length=30)
    file = forms.FileField()
    
    def __init__(self, *args, **kwargs):    
        super(ContactImportForm, self).__init__(*args, **kwargs)        
        self.helper = FormHelper()
        
        
    def clean_file(self):
        content = self.cleaned_data['file']
        content_type = content.content_type#.split('/')[0]
        print(content_type)
        if content_type in settings.ALLOWED_CONTENT_TYPES:
            if content._size > settings.MAX_UPLOAD_FILE_SIZE:
                msg = 'Keep your file size under %s. actual size %s'\
                        % (filesizeformat(settings.MAX_UPLOAD_FILE_SIZE), filesizeformat(content._size))
                raise forms.ValidationError(msg)

            if not (content.name.endswith('.csv') or content.name.endswith('.xlsx') or content.name.endswith('.xls')) :
                msg = 'Your file has to be either .csv, .xls or .xlsx'
                raise forms.ValidationError(msg)
        else:
            raise forms.ValidationError('File not supported')
        
        

class CustomDataIngestForm(forms.Form):
    
    UFDS = (
        ('coid',_("Contact ID")),
        ('doid',_("Domain ID"))
            )
    
    file = forms.FileField()
    unique_field = forms.ChoiceField(choices=UFDS, initial="coid", widget=forms.RadioSelect, label=_("Identity Field"))
    
    def __init__(self, *args, **kwargs):
        super(CustomDataIngestForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
    
    

class OrganizationContactForm(forms.ModelForm):
    
    class Meta:
        model = OrganizationContact
        fields = ['organization','industry','organization_phone_number','address_1','address_2','country','state','city_town']
        widgets = {
            'city_town' : Select2Widget,
            'state': Select2Widget,
            'country':Select2Widget
                   }        
        
class VerifyAccountForm(forms.Form):
    
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    date_of_birth = forms.DateField(required=True, input_formats=settings.DATE_INPUT_FORMATS)
    timezone = TimeZoneField(required=True, widget=Select2Widget(choices=PRETTY_COMMON_TIMEZONES_CHOICES))
    
    email_address = forms.EmailField(disabled=True, required=False)
    phone_number = PhoneNumberField(required=True, help_text="Must be in International format '+234...'")
    email_verification_code = forms.CharField(max_length=28, required=False)
    phone_number_verification_code = forms.CharField(max_length=5, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(VerifyAccountForm, self).__init__(*args, **kwargs)
        self.fields['email_address'].widget = forms.EmailInput(attrs={'value':self.user.email})
        self.fields['first_name'].widget = forms.TextInput(attrs={'value':self.user.first_name})
        self.fields['last_name'].widget = forms.TextInput(attrs={'value':self.user.last_name})
        self.fields['date_of_birth'].initial = self.user.kituser.dob
        self.fields['timezone'].initial = self.user.kituser.timezone
        self.fields['phone_number'].widget = forms.TextInput(attrs={'value':self.user.kituser.phone_number})