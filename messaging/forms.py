'''
Created on Jun 10, 2016

@author: Dayo
'''

from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext
from django.conf import settings

from .models import StandardMessaging, AdvancedMessaging, ReminderMessaging, Reminder, IssueFeedback

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms_foundation.layout import ButtonGroup, ButtonHolder, Div, Hidden,\
                                            Submit, Reset, Button, Layout, Fieldset, Row, Column

from tinymce.widgets import TinyMCE
from django_select2.forms import Select2Widget, Select2MultipleWidget,\
    ModelSelect2MultipleWidget
from django.utils import timezone
from datetime import datetime
from django.forms.models import inlineformset_factory, BaseInlineFormSet




class StandardMessagingForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        
        self.kuser = kwargs.pop('kituser') or None
        
        super(StandardMessagingForm, self).__init__(*args, **kwargs)
        
        self.fields['recipients'].queryset = self.kuser.get_contacts()
        self.fields['smtp_setting'].queryset = self.kuser.get_smtp_items()
        #self.fields['cou_group'].label = "Group Availability"
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_tag = False
        
        self.helper.layout = Layout(
            Row(Column('title'), css_class = "email-title"),
            Row(Column('email_message'), css_class = "email-template"),
            Row(Column('sms_message')),
            HTML('''
                <div class="sms-textarea-status-bar row columns">
                    <div class="column small-4">Length: <span class="length"></span></div>
                    <div class="column small-4">Messages: <span class="messages"></span></div>
                    <div class="column small-4">Remaining: <span class="remaining"></span></div>
                </div>'''
                ), 
            Hidden('message_type', 'STANDARD'),
            Hidden('message_id', '{{messageid}}'),                  
            Fieldset(
                ugettext('Delivery Settings'),
                Row(Column('recipients'), css_class="ss-recipients"),
                Row(
                    Column('copied_recipients', css_class="small-8"),
                    Column(
                        
                        Row('cc_recipients_send_email'),
                        Row('cc_recipients_send_sms'),
                        css_class="small-4",
                        css_id = "cc-recipients-channel-control"),
                    css_id="cc-recipients-select"
                    ),
                Row(Column('delivery_time'), css_class="ss-deliver-at"),
                Div(
                     Row(
                         Column('send_sms', css_class="float-left small-6"),
                         Column('insert_optout', css_class="float-left small-6"),
                         ),
                     Row(Column('sms_sender', css_class="ss-sms-sender")),
                ),
                Row(
                    Column('send_email', css_class="float-left small-6")
                    ),
                Row(Column('smtp_setting'), css_class="ss-smtp-setting"),
                css_class = "new-message-settings-fieldset"
                ),                       
            )    
    
    
    class Meta:
        model = StandardMessaging
        fields = ['title','email_message','sms_message','recipients','copied_recipients','cc_recipients_send_sms',\
                  'cc_recipients_send_email','delivery_time','send_sms', 'send_email', \
                  'sms_sender','smtp_setting','insert_optout']
        widgets = {
            'recipients': Select2MultipleWidget,
            'copied_recipients': Select2MultipleWidget,
            'smtp_setting' : Select2Widget,
            'email_message' : TinyMCE(attrs={'cols': 20,'rows':10}),
            'sms_message' : forms.Textarea(attrs={'rows':5})
        }
        
        
    def clean(self):
        """
        User must Check either Send SMS or Send Email before sending
        """
        cleaned_data = super(StandardMessagingForm, self).clean()
        
        if cleaned_data.get("recipients") == None:
            raise forms.ValidationError('Recipients Cannot be Empty')
        
        send_sms = cleaned_data.get("send_sms", False)
        send_email = cleaned_data.get("send_email", False)
        
        if not (send_sms or send_email):
            #msg = 'You must enter at least a phone number or an email address'
            raise forms.ValidationError(
                'You must select either "Send SMS" or "Send Email", or both.'
                                        )
        if send_sms and not bool(cleaned_data.get('sms_message')):
            raise forms.ValidationError('By checking "send sms", you must create an SMS template')
        
        if send_sms and not cleaned_data.get('sms_sender', False):
            self.add_error('sms_sender', 'SMS Sender is required')
            raise forms.ValidationError('SMS Sender ID is required to send SMS')
        
        if send_email and not bool(cleaned_data.get('email_message')):
            raise forms.ValidationError("Send Email checked, you must create an Email template")

        if send_email and not cleaned_data.get('smtp_setting', False):
            raise forms.ValidationError("Send Email checked, you must select an SMTP server")
        
        if send_email and not bool(cleaned_data.get('title')):
            raise forms.ValidationError("Send Email checked, email should have a Title/Subject")
        
        # clean delivery time
        send_at = cleaned_data.get("delivery_time")
        
        if send_at == None or send_at < timezone.now():
            #raise forms.ValidationError('Your Delivery Date Cannot be in the past')
            cleaned_data["delivery_time"] = datetime.now()
        
        if cleaned_data.get("recipients").count() > settings.MAX_MSG_RECIPIENT:
            raise forms.ValidationError(
                'To check Spam, only {} recipients are allowed. \
                To send to a greater number of recipients, please \
                use the Advanced Messaging'.format(settings.MAX_MSG_RECIPIENT)
                                        )
        
        return cleaned_data   
        
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
        self.helper.layout = Layout(
            Row(Column('title'), css_class = "email-title"),
            Row(
                Column('message_template', css_class = "message-template small-9"),
                Column(
                    Button('preview-template', 'Preview', css_class="small button message-template-preview-btn"), css_class="small-3")
                ),
            Row(Column('custom_data_namespace'), css_class = "custom-data-select"),
            Row(Column('contact_group'), css_class = "contact-group"),
            Row(Column('delivery_time'), css_class = "deliver-at"),
            Row(
                Column('repeat_frequency', css_class="small-6"),
                Column('repeat_until', css_class="small-6")
                ),
            Hidden('message_type', 'ADVANCED'),
            Hidden('message_id', '{{messageid}}')
        )
    
    class Meta:
        model = AdvancedMessaging
        fields = ['title','message_template', 'custom_data_namespace', 'contact_group', 'delivery_time','repeat_frequency','repeat_until']
        widgets = {
            'contact_group': Select2MultipleWidget,
            'message_template' : Select2Widget
        }
        
        
    def clean(self, *args, **kwargs):
        cleaned_data = super(AdvancedMessagingForm, self).clean(*args, **kwargs)
        
        send_at = cleaned_data.get("delivery_time")
        rpt_frq = cleaned_data.get("repeat_frequency")
        rpt_till = cleaned_data.get("repeat_until")
        
        if send_at==None or send_at < timezone.now():
            #raise forms.ValidationError('Your Delivery Date Cannot be in the past')
            cleaned_data["delivery_time"] = datetime.now()
        
        if rpt_frq == 'norepeat':
            rpt_till = None
            
        if rpt_till and rpt_till < send_at:
            raise forms.ValidationError('"Repeat Until" cannot be less than "Deliver at"')
        
        if rpt_frq != 'norepeat' and rpt_till == None:
            raise forms.ValidationError('You need to fill the "Repeat Until" field since you have selected to Repeat this Message')

        
        
        
class ReminderMessagingForm(forms.ModelForm):
    
    date_column = forms.CharField(required=True)
    
    def __init__(self, *args, **kwargs):
    
        self.dcolish = kwargs.pop('date_column_ish','')# or None
        
        super(ReminderMessagingForm, self).__init__(*args, **kwargs)
        
        try:            
            self.fields["date_column"].widget = forms.Select(choices=self.dcolish[0])
            self.fields["date_column"].initial = self.dcolish[1]
        except IndexError:
            print("Must be an ajax submit call where date_column_ish is not provided")
        
        self.fields['contact_group'].label = 'Contact List'
        
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(Column('title'), css_class = "reminder-title"),
            Row(
                Column('message_template', css_class = "message-template small-9"),
                Column(
                    Button('preview-template', 'Preview', css_class="small button message-template-preview-btn"), css_class="small-3")
                ),
            Row(Column('contact_group'), css_class = "contact-group"),            
            Row(
                Column('custom_data_namespace', css_class = "float-left small-6"),
                Column('date_column', css_class = "float-left small-6")
            ),
            Hidden('message_type', 'REMINDER'),
            Hidden('message_id', '{{rmsgid}}')
        )
    
    class Meta:
        model = ReminderMessaging
        fields = ['title','message_template', 'contact_group', 'is_active', 'custom_data_namespace','date_column']
        widgets = {
            'contact_group': Select2MultipleWidget,
            'message_template' : Select2Widget
        }
        
        
    def clean(self, *args, **kwargs):
        cleaned_data = super(ReminderMessagingForm, self).clean(*args, **kwargs)
        
        
        
class ReminderForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        
        super(ReminderForm, self).__init__(*args, **kwargs)        
        self.helper = FormHelper(self)        
        self.helper.attrs = {'data_abide': ''}
        
    
    class Meta:
        model = Reminder
        fields = ['message','delta_value','delta_type','delta_direction']

class BaseReminderFormSet(BaseInlineFormSet):
    def clean(self):
        """Checks that no two reminders have the same values."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        entries = set()
        for form in self.forms:
            
            try:
                #it happens that delta_value key does not exist; and you just want to ignore it
                
                value = form.cleaned_data['delta_value']
                d_type = form.cleaned_data['delta_type']
                d_dir = form.cleaned_data['delta_direction']
                
                fs_item = (value, d_type, d_dir)
            
                if fs_item in entries:
                    raise forms.ValidationError("Reminders must have distinct entries.")
                entries.add(fs_item)
            
                """ check that the values entered are sane """
                if d_type == "day":
                    if not (0 < value <= 7):
                        raise forms.ValidationError('Value for "days" has to be between 1 and 7')
                if d_type == "week":
                    if not (0 < value <= 4.4286):
                        raise forms.ValidationError('Value for "weeks" has to be between 1 and 4.4286')
                if d_type == "month":
                    if not (0 < value <= 12):
                        raise forms.ValidationError('Value for "months" has to be between 1 and 12')
                if d_type == "year":
                    if not (0 < value <= 3):
                        raise forms.ValidationError('Value for "years" has to be between 1 and 3')
            
            except KeyError:
                pass
            
            

        
ReminderFormSet = inlineformset_factory(ReminderMessaging, Reminder, \
                        fields=('delta_value','delta_type','delta_direction'), form = ReminderForm,\
                        formset=BaseReminderFormSet, extra=3, max_num=3, validate_max=True)


        
        
class IssueFeedbackForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(IssueFeedbackForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_id = 'issue-submit-form'
        self.helper.add_input(Submit('submit', _('Submit'), css_id="issue-submit-button", css_class="success float-right"))
        self.helper.add_input(Reset('form_reset', _('Reset'), css_class="float-right"))
    
    class Meta:
        model = IssueFeedback
        fields = ['title','detail','screenshot']