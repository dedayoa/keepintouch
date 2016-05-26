'''
Created on May 23, 2016

@author: Dayo
'''

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import ModelFormMixin
from .models import Contact, Event

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms_foundation.layout import ButtonGroup, ButtonHolder, Submit, Reset, Button, Layout

class ContactForm(forms.ModelForm):
    
    error_css_class = 'alerterror'
    first_name = forms.CharField(label=_('First Name'), widget=forms.TextInput(attrs={'required':''}), required=True)
    
    def __init__(self, *args, **kwargs):
        
        super(ContactForm, self).__init__(*args, **kwargs)
        #had to move the above here from below and also pass self to formhelper to get the layout.append
        #to work
        self.helper = FormHelper(self)        
        self.helper.attrs = {'data_abide': ''}
        self.helper.form_method = 'post'
        
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
        self.helper.add_input(Submit('submit', _('Submit'), css_class="success float-right"))
        self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
        
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
                'You must enter at least a phone number or an email address'
                                        )
    
    class Meta:
        model = Contact
        fields = ['salutation','first_name','last_name','email','phone','active','created_by_group']
        labels = {
            'created_by_group': _('Group'),
        }
        
        
class NewContactForm(forms.ModelForm):
    
    first_name = forms.CharField(label=_('First Name'), widget=forms.TextInput(attrs={'required':''}), required=True)
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.attrs = {'data_abide': ''}
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Submit'), css_class="success float-right"))
        self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
        super(NewContactForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = Contact
        fields = ['salutation','first_name','last_name','email','phone','active','created_by_group']
        labels = {
            'created_by_group': _('Group'),
        }