'''
Created on Jun 10, 2016

@author: Dayo
'''

from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext
from django.conf import settings

from .models import StandardMessaging, AdvancedMessaging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms_foundation.layout import ButtonGroup, ButtonHolder, Div,\
                                            Submit, Reset, Button, Layout, Fieldset, Row, Column

from tinymce.widgets import TinyMCE
from django_select2.forms import Select2Widget, Select2MultipleWidget,\
    ModelSelect2MultipleWidget
from django.utils import timezone




class StandardMessagingForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(StandardMessagingForm, self).__init__(*args, **kwargs)
        
        #self.fields['cou_group'].label = "Group Availability"
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_tag = False
        
        self.helper.layout = Layout(
            Row(Column('email_message'), css_class = "email-template"),
            Row(Column('sms_message')),
            HTML('''
                <div class="sms-textarea-status-bar row columns">
                    <div class="column small-4">Length: <span class="length"></span></div>
                    <div class="column small-4">Messages: <span class="messages"></span></div>
                    <div class="column small-4">Remaining: <span class="remaining"></span></div>
                </div>'''
                ),                     
            Fieldset(
                 ugettext('Sending Settings'),
                 Row(Column('recipients'), css_class="ss-recipients"),
                 Row(Column('delivery_time'), css_class="ss-deliver-at"),
                 Row(
                     Column('send_sms', css_class="float-left small-6"),
                     Column('send_email', css_class="float-left small-6")
                     ),
                 Row(Column('sms_sender', css_class="ss-sms-sender")),
                 Row(Column('smtp_setting'), css_class="ss-smtp-setting"),
                 css_class = "new-message-settings-fieldset"
                 ),                       
            )    
    
    
    class Meta:
        model = StandardMessaging
        fields = ['email_message','sms_message','recipients','delivery_time','send_sms', 'send_email', \
                  'sms_sender','smtp_setting']
        widgets = {
            'recipients': Select2MultipleWidget,
            'smtp_setting' : Select2Widget,
            'email_message' : TinyMCE(attrs={'cols': 20,'rows':10}),
            'sms_message' : forms.Textarea(attrs={'rows':5})
        }
        
        
    def clean(self):
        """
        User must Check either Send SMS or Send Email before sending
        """
        cleaned_data = super(StandardMessagingForm, self).clean()
        send_sms = cleaned_data.get("send_sms")
        send_email = cleaned_data.get("send_email")
        
        if not (send_sms or send_email):
            #msg = 'You must enter at least a phone number or an email address'
            raise forms.ValidationError(
                'You must select either "Send SMS" or "Send Email", or both.'
                                        )
        
        send_at = cleaned_data.get("delivery_time")
        if send_at < timezone.now():
            raise forms.ValidationError('Your Delivery Date Cannot be in the past')
        
        if cleaned_data["recipients"].count() > settings.MAX_MSG_RECIPIENT:
            raise forms.ValidationError(
                'To check Spam, only {} recipients are allowed. \
                To send to a greater number of recipients, please \
                use the Advanced Messaging'.format(settings.MAX_MSG_RECIPIENT)
                                        )
            
        
    '''      
    def clean_delivery_time(self):
        
        super(StandardMessagingForm, self).clean()
        send_at = self.cleaned_data.get("delivery_time")
        if send_at < timezone.now():
            msg = 'Your Delivery Date Cannot be in the past'
            self.add_error('delivery_time', msg)
    '''
            
            
            
class AdvancedMessagingForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(AdvancedMessagingForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_tag = False
    
    class Meta:
        model = AdvancedMessaging
        fields = ['title','message_template', 'contact_group', 'delivery_time']
        widgets = {
            'contact_group': Select2MultipleWidget,
            'message_template' : Select2Widget
        }
        