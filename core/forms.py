'''
Created on May 23, 2016

@author: Dayo
'''

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import ModelFormMixin
from .models import Contact, Event

from crispy_forms.helper import FormHelper
from crispy_forms_foundation.layout import Layout, ButtonGroup, ButtonHolder, Submit, Reset

class ContactForm(forms.ModelForm):
    
    error_css_class = 'alerterror'
    first_name = forms.CharField(label=_('First Name'), widget=forms.TextInput(attrs={'required':''}), required=True)
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.attrs = {'data_abide': ''}
        self.helper.form_method = 'post'
        self.helper.add_input(Reset('delete', _('Delete'), css_class="alert"))
        self.helper.add_input(Reset('reset', _('Reset')))
        self.helper.add_input(Submit('submit', _('Submit'), css_class="success"))
        super(ContactForm, self).__init__(*args, **kwargs)
        
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
        self.helper.add_input(Reset('reset', _('Reset')))
        self.helper.add_input(Submit('submit', _('Submit'), css_class="success"))
        super(NewContactForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = Contact
        fields = ['salutation','first_name','last_name','email','phone','active','created_by_group']
        labels = {
            'created_by_group': _('Group'),
        }