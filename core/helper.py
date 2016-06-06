'''
Created on May 27, 2016

@author: Dayo
'''

from crispy_forms.helper import FormHelper

class EventFormSetHelper(FormHelper):
    
    def __init__(self, *args, **kwargs):
        super(EventFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        

from django.core.mail import send_mail

class TestSMTPSetting():
    pass