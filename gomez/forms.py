'''
Created on Jul 26, 2016

@author: Dayo
'''
from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms_foundation.layout import ButtonGroup, ButtonHolder, Div,\
                                            Submit, Reset, Button, Layout, Fieldset, Row, Column
                                            
from .models import KITSystem

class SystemSettingsForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(SystemSettingsForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_tag = True
        self.helper.add_input(Submit('submit', _('Update'), css_class="success float-right"))
        self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
        self.fields['did_number'].disabled = True
    
    class Meta:
        model = KITSystem
        fields = ['company_wide_contacts', 'default_sms_sender','sms_unsubscribe_message','did_number',\
                  'max_standard_message']
        widgets = {
            'sms_unsubscribe_message' : forms.Textarea(attrs={'rows':5, 'cols': 30})
                   }


    