'''
Created on Jul 20, 2016

@author: Dayo
'''

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime

from ..tasks import process_onetime_event, process_private_anniversary, process_public_anniversary
from core.models import Event, Contact, MessageTemplate, KITUser, SMTPSetting


class PrivateAnniversaryTests(TestCase):
    
    
    @classmethod
    def setUpTestData(cls):
        # create due private event
        
        user = User.objects.create_user('dayo', 'dayo@windom.biz', 'xHD192zaq')
        parent = User.objects.create_user('mradmin', 'dedayoa@gmail.com', 'password14')
        kituser = KITUser.objects.create(
                    user = user,
                    dob = '20-07-1990',
                    timezone = 'Africa/Lagos',
                    parent = parent,
                    phone_number = '+2348160478727',
                    industry = 'OTHER',
                    address_1 = '6, Yomi Ogunkoya',
                    city_town = 'Ologuneru',
                    state = 'OYO',
                    is_admin = False,
                    )
        
        contact = Contact.objects.create(
                salutation = 'mr',
                first_name = 'Adedayo',
                last_name = 'Ayeni',
                email = 'dayo@windom.biz',
                phone = '+2348028443225',
                kit_user = kituser
            )
        
        smtp = SMTPSetting.objects.create(
            description = 'Default',
            from_user = 'dedayoa@gmail.com',
            smtp_server = 'rsb18.rhostbh.com',
            smtp_port = 465,
            connection_security = 'SSLTLS',
            smtp_user = 'dayo@windom.biz',
            smtp_password = 'Password2014',
            active = True,         
            kit_admin = parent
            )
        
        message_template = MessageTemplate.objects.create(
                title = 'Test Template Title',
                email_template = 'Email Template',
                sms_template = 'SMS Template',
                sms_sender = 'Test SMS',
                smtp_setting = smtp,
                send_sms = True,
                send_email = True,
            )
        cls.dpe = Event.objects.create(
                    contact = contact,
                    date = datetime.utcnow(),
                    message = message_template,
                    title = 'My Birthday',
                    last_run = '20-07-2015'
                                       )
    
    def test_process_private_anniversary(self):
        
        pass