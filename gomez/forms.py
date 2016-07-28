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
                                            
from .models import KITSystem, IssueFeedback

class SystemSettingsForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(SystemSettingsForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_tag = True
        self.helper.add_input(Submit('submit', _('Update'), css_class="success float-right"))
        self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
    
    class Meta:
        model = KITSystem
        fields = ['company_wide_contacts']  
        
        
class IssueFeedback(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(IssueFeedback, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_tag = True
        self.helper.add_input(Submit('submit', _('Submit'), css_class="success float-right"))
        self.helper.add_input(Reset('reset', _('Reset'), css_class="float-right"))
    
    class Meta:
        model = IssueFeedback
        fields = ['title','detail','screenshot']