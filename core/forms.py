'''
Created on May 23, 2016

@author: Dayo
'''

from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Contact, Event

from crispy_forms.helper import FormHelper
from crispy_forms_foundation.layout import Layout, ButtonGroup, ButtonHolder, Submit, Reset

class ContactForm(forms.ModelForm):
    
    first_name = forms.CharField(label=_('First Name'), widget=forms.TextInput(attrs={'required':''}), required=True)
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.attrs = {'data_abide': ''}
        self.helper.form_method = 'post'
        self.helper.add_input(Reset('reset', _('Reset')))
        self.helper.add_input(Submit('submit', _('Submit'), css_class="success"))
        super(ContactForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = Contact
        fields = ['salutation','first_name','last_name','email','phone','active','created_by_group']
        labels = {
            'created_by_group': _('Group'),
        }