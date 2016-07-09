'''
Created on May 23, 2016

@author: Dayo
'''

from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext
from django.views.generic.edit import ModelFormMixin
from django.forms.models import formset_factory, inlineformset_factory
from django.conf import settings


from .models import Contact, Event, PublicEvent, MessageTemplate, KITUser, SMTPSetting, ContactGroup
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

class ContactForm(forms.ModelForm):
    
    error_css_class = 'alerterror'
    first_name = forms.CharField(label=_('First Name'), widget=forms.TextInput(attrs={'required':''}), required=True)
    
    def __init__(self, *args, **kwargs):
        
        super(ContactForm, self).__init__(*args, **kwargs)
        #had to move the above here from below and also pass self to formhelper to get the layout.append
        #to work
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
        fields = ['salutation','first_name','last_name','email','phone','active']
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
        fields = ['salutation','first_name','last_name','email','phone','active']
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
                 css_class = "new-template-settings-fieldset"
                 ),                       
            )
    
    class Meta:
        model = MessageTemplate
        fields = ['title', 'email_template', 'sms_template', 'active', 'cou_group', \
                  'smtp_setting', 'send_sms','send_email']        
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
        fields = ['username','email','first_name','last_name',\
                  'is_active'
                  ]  
        
class NewUserForm(forms.ModelForm):
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    
    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_tag = False
    
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
        fields = ['dob','phone_number','industry','company','address_1',\
                  'address_2','city_town','state']
        exclude = ['user']
        widgets = {
            'state': Select2Widget,
                   }
        
        
        
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
        
        super(UserGroupSettingForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', _('Submit'), css_class="success float-right"))
        self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
    
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
        
        super(ContactGroupForm, self).__init__(*args, **kwargs)
        
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