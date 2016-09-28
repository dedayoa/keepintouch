'''
Created on Jun 15, 2016

@author: Dayo
'''

from django.template import Context, Template, loader
from django.apps import apps
import logging
import django_rq

from django.utils import timezone
from django.conf import settings

from .helper import SMTPHelper, SMSHelper, get_next_delivery_time, OKToSend
from core.exceptions import *
from core.models import Contact, PublicEvent, KITUser, SMTPSetting, Event, CustomData
from dateutil.relativedelta import relativedelta
import arrow

from .models import QueuedMessages, ProcessedMessages,RunningMessage, IssueFeedback, FailedKITMessage

from .templates import TemplateForIssueFeedbackMessages, TemplateForPhoneEmailVerification

from gomez.models import KITSystem
from core.googlext import GoogleURLShortener
from django.core.urlresolvers import reverse

#SMTPSetting = apps.get_model('core','SMTPSetting')

def _compose(template, convars, custom_convars = {}):
    # This composes the message using the template and the context variables
    # users cannot override the default_convars for contacts
    
    t = Template(template)
    context_vars = custom_convars 
    
    default_convars = {
                        'firstname':getattr(convars,'first_name',''),
                        'lastname':getattr(convars,'last_name',''),
                        'salutation':getattr(convars,'salutation',''),
                        'email':getattr(convars,'email',''),
                        'phone':getattr(convars,'phone',''),                            
                        }
    context_vars.update(default_convars)
    
    return t.render(Context(context_vars))



@django_rq.job('email')
def _send_email(email_message, smtp_profile, **kwargs):
    es = SMTPHelper(smtp_profile)
    es.send_email(email_message, **kwargs)

@django_rq.job('sms')
def _send_sms(sms_message, kuser, msg_type, batch_id=''):
    es = SMSHelper(sms_message, kuser, msg_type, batch_id)
    es.send_my_sms()


def process_private_anniversary(private_events=None):
    #get anniversaries that occur today and which have not been handled
    if private_events:
        due_private_events = private_events
    else:
        due_private_events = Event.objects.select_related('contact','message').filter(date__day = timezone.now().day,
                                                                      date__month = timezone.now().month,
                                                                      last_run__year__lte = timezone.now().year)
    # For each due private anniversary, prepare email and sms
    
    for peven in due_private_events:
        try:
            ok_to_send = OKToSend(peven.contact.kit_user)
            if ok_to_send.check():
                if peven.message.send_email and peven.contact.email and peven.message.email_template:
                    etempl = _compose(peven.message.email_template, peven.contact) #compose title
                    rttempl = _compose(peven.message.title, peven.contact) #compose message
                    _send_email.delay([rttempl,etempl,peven.contact.email],\
                                              peven.message.smtp_setting.values(),\
                                              owner = peven.contact.kit_user
                                              )
                    
                if peven.message.send_sms and peven.contact.phone and peven.message.sms_template:
                    sms_msg = _compose(peven.message.sms_template, peven.contact)
                    sender = _compose(peven.message.sms_sender, peven.contact)
                    _send_sms.delay([sender,sms_msg,peven.contact.phone.as_e164],\
                                            peven.contact.kit_user,
                                            'private_anniv_msg',
                                            )
                # update the last run date (year especially)
                peven.last_run=timezone.now().date()
                peven.save()
        # move messages to a paused queue pending when error is resolved
        # also, send user a message about the issue
        except IsNotActiveError as e:
            FailedKITMessage.objects.create(
                    message_data = [peven],
                    message_category = 'private_anniv_msg',
                    reason = e.message,
                    owned_by = peven.contact.kit_user
                                            )
        except NoActiveSubscriptionError as e:
            FailedKITMessage.objects.create(
                    message_data = [peven],
                    message_category = 'private_anniv_msg',
                    reason = e.message,
                    owned_by = peven.contact.kit_user
                                            )
        except FailedSendingMessageError as e:
            FailedKITMessage.objects.create(
                    message_data = [peven],
                    message_category = 'private_anniv_msg',
                    reason = e.message,
                    owned_by = peven.contact.kit_user
                                            )
             
    
    
def process_public_anniversary(public_events=None):
    #get anniversaries that occur today
    if public_events:
        due_public_events = public_events
    else:
        due_public_events = PublicEvent.objects.select_related('message').filter(date = timezone.now().date())
    # For each due private anniversary,
    for publicevent in due_public_events:
        for recipient_d in publicevent.get_recipients():
            try:
                ok_to_send = OKToSend(publicevent.kit_user)
                if ok_to_send.check():
                    if publicevent.message.send_email and recipient_d.email and publicevent.message.email_template:
                        e_msg = _compose(publicevent.message.email_template, recipient_d)
                        e_title = _compose(publicevent.message.title, recipient_d)
                        _send_email.delay([e_title,e_msg,recipient_d.email],\
                                          publicevent.message.smtp_setting.values(),\
                                          owner = publicevent.kit_user
                                          )
                        
                    if publicevent.message.send_sms and recipient_d.phone and publicevent.message.sms_template:
                        s_msg = _compose(publicevent.message.sms_template, recipient_d)
                        s_sender = _compose(publicevent.message.sms_sender, recipient_d)
                        _send_sms.delay([s_sender,s_msg,recipient_d.phone.as_e164],\
                                        publicevent.kit_user,
                                        'public_anniv_msg',
                                        )
            except IsNotActiveError as e:
                FailedKITMessage.objects.create(
                        message_data = [publicevent],
                        message_category = 'public_anniv_msg',
                        reason = e.message,
                        owned_by = publicevent.kit_user
                                                )
            except NoActiveSubscriptionError as e:
                FailedKITMessage.objects.create(
                        message_data = [publicevent],
                        message_category = 'public_anniv_msg',
                        reason = e.message,
                        owned_by = publicevent.kit_user
                                                )
            except FailedSendingMessageError as e:
                FailedKITMessage.objects.create(
                        message_data = [publicevent],
                        message_category = 'public_anniv_msg',
                        reason = e.message,
                        owned_by = publicevent.kit_user
                                                )
            
        publicevent.date = timezone.now().date()+relativedelta(years=1)
        publicevent.save()
    
def process_onetime_event(queued_messages=None):
    
    if queued_messages:
        due_queued_messages = queued_messages
    else:
        due_queued_messages = QueuedMessages.objects.filter(delivery_time__lte = timezone.now())
    
    gurli = GoogleURLShortener()
    
    for queued_message in due_queued_messages:
        recipients_qs = Contact.objects.filter(pk__in = queued_message.message["recipients"])
        
        if queued_message.message["others"].get("cc_recipients"):
            cc_recipients_qs = Contact.objects.filter(pk__in = queued_message.message["others"]["cc_recipients"])
            cc_emails = [x[0] for x in cc_recipients_qs.values_list('email')] #get a list of emails
        else:
            cc_emails = []
        
        
        # create entry in processed message
        sprm = ProcessedMessages.objects.create(
            message_type = queued_message.message_type,
            message = queued_message.message,
            created_by = queued_message.created_by
        )
        
        
        for recipient_d in recipients_qs:
            try:
                ok_to_send = OKToSend(queued_message.created_by)
                if ok_to_send.check():
                    #custom data
                    if queued_message.message["others"].get("custom_data_namespace"):
                        cd_data = (CustomData.objects.get(namespace=queued_message.message["others"].get("custom_data_namespace", None))).data
                        cdd = cd_data.get(recipient_d.slug) #get the value of the contactid key/slug
                    else:
                        cdd = {}
                    
                    #email
                    if queued_message.message["send_email"] and recipient_d.email and queued_message.message["email_template"]:
                        smtp_setting_qsv = SMTPSetting.objects.get(pk = queued_message.message["smtp_setting_id"])
                        e_msg = _compose(queued_message.message["email_template"], recipient_d, cdd)
                        e_title = _compose(queued_message.message["title"], recipient_d, cdd)
                        _send_email.delay([e_title, e_msg, recipient_d.email],\
                                          smtp_setting_qsv, cc_recipients = cc_emails, owner = queued_message.created_by
                                          )
                    #sms   
                    if queued_message.message["send_sms"] and recipient_d.phone and queued_message.message["sms_template"]:
                        
                        s_sender = _compose(queued_message.message["sms_sender_id"], recipient_d)
                        
                        if queued_message.message["sms_insert_optout"] == True:
                            # append the opt out text and link to each SMS
                            full_tpl = '{} {}'.format(
                                                queued_message.message["sms_template"],
                                                gurli.get_short_url("{}/sms/unsubscribe/?coid={}&ptid={}&prcmid={}".\
                                                                    format(settings.WEBHOOK_BASE_URL, recipient_d.slug, queued_message.created_by.parent.id,sprm.id))
                                                )
                            s_msg = _compose(full_tpl, recipient_d, cdd)
                        else:
                            s_msg = _compose(queued_message.message["sms_template"], recipient_d, cdd)
                            
                        _send_sms.delay([s_sender, s_msg, recipient_d.phone.as_e164],\
                                         queued_message.created_by,
                                         'one_time_msg',
                                         batch_id = sprm.id
                                          )
                        
            except IsNotActiveError as e:
                FailedKITMessage.objects.create(
                        message_data = [queued_message],
                        message_category = 'queued_msg',
                        reason = e.message,
                        owned_by = queued_message.created_by
                                                )
            except NoActiveSubscriptionError as e:
                FailedKITMessage.objects.create(
                        message_data = [queued_message],
                        message_category = 'queued_msg',
                        reason = e.message,
                        owned_by = queued_message.created_by
                                                )
            except FailedSendingMessageError as e:
                FailedKITMessage.objects.create(
                        message_data = [queued_message],
                        message_category = 'queued_msg',
                        reason = e.message,
                        owned_by = queued_message.created_by
                                                )
            except CustomData.DoesNotExist:
                FailedKITMessage.objects.create(
                        message_data = [queued_message],
                        message_category = 'queued_msg',
                        reason = 'The Custom Data "%s" being referenced is no longer Available'%(due_queued_messages.message["custom_data_id"]),
                        owned_by = queued_message.created_by
                                                )
        

        
        # delete queued message from queuedmessage table if it does not reccur
        if queued_message.recurring == False:
            queued_message.delete()
        elif queued_message.recurring == True and (arrow.get(queued_message.message["others"]["repeat_until"],'DD-MM-YYYY HH:mm').datetime <= timezone.now()):
            # if it's a recurring message and repeat_until becomes less than now
            queued_message.delete()
        else:
            queued_message.delivery_time=get_next_delivery_time(queued_message.message["others"]["repeat_frequency"],\
                                                                       queued_message.delivery_time)
            queued_message.save()

        


def process_reminder_event(running_messages=None):
    
    # get messages to run today
    if running_messages:
        all_running_messages = running_messages
    else:
        all_running_messages = RunningMessage.objects.filter(completed=False)
        
    # create processedmessage
    
    for running_message in all_running_messages:        
        messages_due_today = running_message.get_events_due_within_the_next_day()
        if messages_due_today == []:
            continue
        for message_due in messages_due_today:
            
            message = message_due[0]
            created_by = KITUser.objects.get(pk=message_due[4])
            recipient_d = Contact.objects.get(pk=message_due[1])
            
            try:
                ok_to_send = OKToSend(created_by)
                if ok_to_send.check():
                    #custom data
                    if message["others"]["custom_data_namespace"]:
                        cd_data = (CustomData.objects.get(namespace=message["others"]["custom_data_namespace"])).data
                        cdd = cd_data.get(recipient_d.slug)
                        
                    #email
                    if message["send_email"] and recipient_d.email and message["email_template"]:
                        smtp_setting_qsv = SMTPSetting.objects.get(pk = message["smtp_setting_id"])
                        e_msg = _compose(message["email_template"], recipient_d, cdd)
                        e_title = _compose(message["title"], recipient_d, cdd)
                        _send_email.delay([e_title, e_msg, recipient_d.email],\
                                          smtp_setting_qsv, owner = created_by
                                          )
                    #sms
                    if message["send_sms"] and recipient_d.phone and message["sms_template"]:
                        s_msg = _compose(message["sms_template"], recipient_d, cdd)
                        s_sender = _compose(message["title"], recipient_d, cdd)
                        _send_sms.delay([s_sender, s_msg, recipient_d.phone.as_e164],\
                                        created_by,
                                        'reminder_msg',
                                          )
                        
            except IsNotActiveError as e:
                FailedKITMessage.objects.create(
                        message_data = [running_message],
                        message_category = 'running_msg',
                        reason = e.message,
                        owned_by = created_by
                                                )
            except NoActiveSubscriptionError as e:
                FailedKITMessage.objects.create(
                        message_data = [running_message],
                        message_category = 'running_msg',
                        reason = e.message,
                        owned_by = created_by
                                                )
            except FailedSendingMessageError as e:
                FailedKITMessage.objects.create(
                        message_data = [running_message],
                        message_category = 'running_msg',
                        reason = e.message,
                        owned_by = created_by
                                                )
            except CustomData.DoesNotExist:
                FailedKITMessage.objects.create(
                        message_data = [running_message],
                        message_category = 'running_msg',
                        reason = 'The Custom Data "%s" being referenced is no longer Available'%(message["others"]["custom_data_namespace"]),
                        owned_by = created_by
                                                )
 
                

        
def process_system_notification(**kwargs):
    
    tmpl = TemplateForIssueFeedbackMessages()
    
    template_to_user = tmpl.template_to_user()
    template_to_dev_chan = tmpl.template_to_dev_chan()
    
    t = Template(template_to_user)
    email_to_user = t.render(Context(
                                {
                            'fullname':kwargs.get('fullname',''),
                                 }
                                     )
                             )
    u = Template(template_to_dev_chan)
    email_to_support = u.render(Context(
                                {
                            'fullname': kwargs.get('fullname',''),
                            'email': kwargs.get('submitter_email',''),
                            'title': kwargs.get('title',''),
                            'detail': kwargs.get('detail',''),
                            'screenshot_link': kwargs.get('attachment',''),
                                 }    
                                        )
                                )
    
    smtp_settings = SMTPSetting(**settings.SUPPORT_EMAIL)
    
    _send_email.delay(['Feedback Received!', email_to_user, kwargs.get('submitter_email','')],
                      smtp_settings,
                       owner = kwargs.get('submitter_kusr',''), #current admin
                      )
    #_send_sms.delay(["IssueReport", "New Issue Submitted", "+2348028443225"],
    #                KITUser.objects.get(pk=settings.SYSTEM_KITUSER_ID),
    #                'system_msg'
    #                )
    
    _send_email.delay(['Bug Feedback from website!', email_to_support, 'bugs@intouchng.com'],
                      smtp_settings,
                      owner = KITUser.objects.get(pk=settings.SYSTEM_KITUSER_ID) #current admin
                      )


def process_verification_messages(**kwargs):
    
    tmpl = TemplateForPhoneEmailVerification()
    
    
    if not kwargs.get('email_is_validated'):
        email_template = 'emails/user_email_address_verification.html'
        
        # create link in email
        email_verification_link = "{}{}?email={}&t={}".format(settings.WEBHOOK_BASE_URL,\
                                            reverse('core:register-validate-email'),kwargs.get('email'),\
                                            kwargs.get('email_verification_link'))
        
        email_to_user = loader.get_template(email_template).render(Context({
                                'fullname':kwargs.get('fullname',''),
                                'email_verification_link': email_verification_link
                                     })
                                 )
        smtp_settings = SMTPSetting(**settings.SUPPORT_EMAIL)
        _send_email(['Email Verification Code', email_to_user, kwargs.get('email','')],
                          smtp_settings,
                          owner = KITUser.objects.get(pk=settings.SYSTEM_KITUSER_ID),
                          )
        
    if not kwargs.get('phone_is_validated'):    
        template_sms = tmpl.template_sms()   
        stmpl = Template(template_sms)
        sms_to_user = stmpl.render(Context({
                                'fullname':kwargs.get('fullname',''),
                                'phone_verification_code': kwargs.get('phone_verification_code','')
                                     })
                                    )
    
        _send_sms.delay(["In.Touch NG", sms_to_user, (kwargs.get('phone_number')).as_e164],
                        KITUser.objects.get(pk=settings.SYSTEM_KITUSER_ID),
                        'system_msg',                     
                        )
