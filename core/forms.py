'''
Created on May 23, 2016

@author: Dayo
'''

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import ModelFormMixin
from django.forms.models import formset_factory, inlineformset_factory
from django.conf import settings


from .models import Contact, Event, PublicEvent, MessageTemplate
from .helper import EventFormSetHelper


from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms_foundation.layout import ButtonGroup, ButtonHolder, Submit, Reset, Button, Layout
from django_select2.forms import Select2Widget, Select2MultipleWidget,\
    ModelSelect2MultipleWidget

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
        fields = ['title','date','message','recipients']
        widgets = {
            'recipients': Select2MultipleWidget,
            'message' : Select2Widget
        }  
        
        
class MessageTemplateForm(forms.ModelForm):
    
    
    
    def __init__(self, *args, **kwargs):
        super(MessageTemplateForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', _('Submit'), css_class="success float-right"))
        self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
    
    class Meta:
        model = MessageTemplate
        fields = ['title', 'email_template', 'sms_template', 'cou_group', 'smtp_setting', 'send_sms']