'''
Created on Jul 13, 2016

@author: Dayo
'''
import os, sys
import pickle
import tablib
import json
import uuid
import datetime, pytz, dateutil.parser, arrow
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax
from django.template import Context, Template
#from django.utils.crypto import get_random_string
from django.db import transaction
from django.conf import settings

from .models import StandardMessaging, QueuedMessages, AdvancedMessaging,\
                    RunningMessage, ReminderMessaging, event_date
from core.models import CustomData, Contact, SMTPSetting, MessageTemplate, ContactGroup                   

from messaging.sms_counter import SMSCounter

from .forms import StandardMessagingForm, AdvancedMessagingForm, ReminderMessagingForm, ReminderFormSet,\
                    IssueFeedbackForm
from .helper import get_next_delivery_time 
import base64
from cryptography.fernet import Fernet

from gomez.models import KITSystem


def _compose(template, convars):
    
    t = Template(template)
    return t.render(Context({
                            'firstname':getattr(convars,'first_name',''),
                            'lastname':getattr(convars,'last_name',''),
                            'salutation':getattr(convars,'salutation',''),
                            'email':getattr(convars,'email',''),
                            'phone':getattr(convars,'phone',''),                            
                            })
                    )


def _tokenize(file_path):
    
    aix = bytes(settings.SECRET_KEY[:32],'utf-8')
    f = Fernet(base64.urlsafe_b64encode(aix))
    token = f.encrypt(bytes(file_path,'utf-8'))
    
    return token

def _untokenize(enc_file_loc):
    
    aix = bytes(settings.SECRET_KEY[:32],'utf-8')
    f = Fernet(base64.urlsafe_b64encode(aix))
    file_loc = (f.decrypt(bytes(enc_file_loc,'utf-8'))).decode('utf-8')
    
    return file_loc

@ajax
@login_required
def prepare_to_send_message(request):
    #c = "foo " + request.POST['recipients']
    #return {'result': c}
    
    if request.method == 'POST':
        #return {'result':request.POST.getlist('recipients',[])}
        #get contacts

        if request.POST.get('message_type') == 'STANDARD':
            myform = StandardMessagingForm(request.POST, kituser = request.user.kituser)  
            if not myform.is_valid():
                return {'errors':myform.errors.as_json(escape_html=True)}
            else:
                recipients = request.POST.getlist('recipients',None)
                cts = Contact.objects.filter(pk__in=recipients)
                result_dict = {}
            
                #Return: "Email will be sent to (38) recipients"
                
                if request.POST.get('send_email', False):
                    #I need the number of recipients who have emails accounts registered on the system
                    num_of_contacts_with_emails = cts.exclude(email__exact='').count()
                    
                    smtp_to_use = SMTPSetting.objects.get(pk=request.POST.get('smtp_setting',''))
                    
                    result_dict['nocwe'] = num_of_contacts_with_emails
                    result_dict['mail_server'] = '<a href="{}" target="_blank">{}</a>'.\
                                                format(smtp_to_use.get_absolute_url(),smtp_to_use.smtp_server)            
                    result_dict['sample_email'] = _compose(request.POST.get('email_message'),cts.first()) #convert to img
                    result_dict['sample_email_title'] = _compose(request.POST.get('title'),cts.first())
                    #code_seg_1 = get_random_string(length=10)
                
                else:
                    result_dict['nocwe'] = 0 #if this is 0, then it all dont matter
                
                #Return: Total SMSs to be sent (200), Send Units Available (550)
                 
                if request.POST.get('send_sms', False):
                    m_count = 0
                    
                    contacts_with_phone = cts.exclude(phone__exact = '')
                    
                    for contact in contacts_with_phone:
                        mc_var = SMSCounter().get_messages_count_only(_compose(request.POST.get('sms_message'), contact))
                        m_count+=mc_var
                        
                    result_dict['total_sms_count'] = m_count
                    result_dict['sample_sms'] = _compose(request.POST.get('sms_message'),cts.first())
                    #code_seg_2 = get_random_string(length=10)
                    
                else:
                    result_dict['total_sms_count'] = 0
                
                #result_dict['idtdt'] = idondit = "{}{}".format(code_seg_1, code_seg_2)
                
                # the global is failing, switching to pickle + uuid
                file_path = os.path.join(settings.MEDIA_ROOT, 'tmp/'+str(uuid.uuid4()))
                
                with open(file_path, 'wb') as f:
                    pickle.dump(myform, f, pickle.HIGHEST_PROTOCOL)
                
                result_dict['msgtoken'] = _tokenize(file_path)
                     
                return {'result':result_dict}
            
        elif request.POST.get("message_type") == 'ADVANCED':
            
            adv_msg_form = AdvancedMessagingForm(request.POST)
            if not adv_msg_form.is_valid():
                return {'errors':adv_msg_form.errors.as_json(escape_html=True)}
            else:
                recipient_group = request.POST.getlist('contact_group',[])
                message_template = request.POST.get('message_template')
                
                result_dict = {}
                
                grps = ContactGroup.objects.filter(pk__in = recipient_group).prefetch_related('contacts')
                contacts = set() #it can happen that a contact is in multiple groups. By using sets, the customer will get just 1 message
                
                msg_t = request.user.kituser.get_templates().get(pk = message_template)
                #MessageTemplate.objects.get(pk = message_template, cou_group__in = request.user.kituser.groups_belongto)
                for grp in grps:
                    for contacts_per_group in grp.contacts.all():
                        contacts.add(contacts_per_group)
                del grps #free memory, maybe
                
                if msg_t.send_email == True:
                    #I need the number of recipients who have emails accounts registered on the system
                    num_of_contacts_with_emails = 0 #cts.exclude(email__exact='').count()
                    
                    for contact in contacts:
                        if contact.email != '':
                            num_of_contacts_with_emails+=1
                    
                    smtp_to_use = msg_t.smtp_setting
                    
                    result_dict['nocwe'] = num_of_contacts_with_emails
                    result_dict['mail_server'] = '<a href="{}" target="_blank">{}</a>'.\
                                                format(smtp_to_use.get_absolute_url(),smtp_to_use.smtp_server)
                    ## get any contact, and add it back
                    elem = contacts.pop()
                    contacts.add(elem)
                    ##                 ##
                    
                    a_contact = elem    
                    result_dict['sample_email'] = _compose(msg_t.email_template,a_contact) #convert to img
                    result_dict['sample_email_title'] = _compose(msg_t.title,a_contact)
                    #code_seg_1 = get_random_string(length=10)
                
                else:
                    result_dict['nocwe'] = 0 #if this is 0, then it all dont matter
                
                #Return: Total SMSs to be sent (200), Send Units Available (550)
                 
                if msg_t.send_sms == True:
                    
                    m_count = 0                    
                    for contact in contacts:
                        if contact.phone != '':
                            mc_var = SMSCounter().get_messages_count_only(_compose(msg_t.sms_template,contact))
                            m_count+=mc_var
                    
                    ## get any contact
                    elem = contacts.pop()
                    contacts.add(elem)
                    ##                 ##                       
                    
                    a_contact = elem 
                    result_dict['total_sms_count'] = m_count
                    result_dict['sample_sms'] = _compose(msg_t.sms_template,a_contact)
                    #code_seg_2 = get_random_string(length=10)
                    
                else:
                    result_dict['total_sms_count'] = 0
                
                recipient = []
                for r in contacts:
                    recipient.append(r.pk)
                    
                my_adv_form = [adv_msg_form, recipient, msg_t]
                
                file_path = os.path.join(settings.MEDIA_ROOT, 'tmp/'+str(uuid.uuid4()))
                
                with open(file_path, 'wb') as f:
                    pickle.dump(my_adv_form, f, pickle.HIGHEST_PROTOCOL)
                
                result_dict['msgtoken'] = _tokenize(file_path)
                #result_dict['idtdt'] = idondit = "{}{}".format(code_seg_1, code_seg_2)       
                return {'result':result_dict} 
            


def time_to_utc(mytime):
    # primarily for dates that will be stored as json
    # django automatically converts between localtime and UTC for DB
    return  (arrow.get(mytime).to('UTC')).datetime             
    

@ajax
@login_required
@transaction.atomic
def send_message(request):
    
    if request.method == 'POST':
        
        # remove message from draft if it has been drafted
        if request.POST.get("message_type") == 'STANDARD':
            
            try:
                #delete item from draft
                if StandardMessaging.objects.filter(pk = request.POST.get('message_id')).exists():
                    created_time = (StandardMessaging.objects.values('created').get(pk = request.POST.get('message_id')))['created']
                    messageid = request.POST.get('message_id')
            except ValueError: #messageid is empty
                created_time = None
                messageid = 0
            # send message to queue table
            token = request.POST.get("msgtoken")
            pkl_loc = _untokenize(token)
            with open(pkl_loc, 'rb') as f:
                myform = pickle.load(f)
                
            if myform.cleaned_data.get('insert_optout') == True:
                sms_t = '{}\n{}'.format(myform.cleaned_data.get('sms_message'),\
                                        KITSystem.objects.get(kit_admin=request.user.kituser.parent).sms_unsubscribe_message,
                                        )
            else:
                sms_t = myform.cleaned_data.get('sms_message','')
            
            QueuedMessages.objects.create(
                message_type = request.POST.get("message_type"),
                message_id = messageid, #-1 means it was never saved to draft
                message = {
                    'message_id' : messageid,
                    'title' : myform.cleaned_data.get('title',''),
                    'email_template' : myform.cleaned_data.get('email_message',''),
                    'sms_template' : sms_t,
                    'send_email' : myform.cleaned_data.get('send_email', False),
                    'send_sms' : myform.cleaned_data.get('send_sms', False),
                    'sms_insert_optout' : myform.cleaned_data.get('insert_optout', False),
                    'sms_sender_id' : myform.cleaned_data.get('sms_sender',''),
                    'recipients' : request.POST.getlist('recipients',[]),
                    'smtp_setting_id': request.POST.get('smtp_setting',''),
                    'others' : {
                            'draft_title' : myform.cleaned_data.get('title',''),
                            'original_created' : created_time.strftime('%d-%m-%Y %H:%M') if created_time else None,
                            'cc_recipients' : request.POST.getlist('copied_recipients',[]),
                            'cc_recipients_send_sms' : myform.cleaned_data.get('cc_recipients_send_sms', False),
                            'cc_recipients_send_email' : myform.cleaned_data.get('cc_recipients_send_email', False),                         
                                }
                            },
                delivery_time = myform.cleaned_data.get('delivery_time'),
                created_by = request.user.kituser
                
            )
            
            return {'result':'Success! Message Queued for Sending'}
            
        elif request.POST.get("message_type") == 'ADVANCED':
            
            
            try:
                #delete item from draft
                if AdvancedMessaging.objects.filter(pk = request.POST.get('message_id')).exists():
                    created_time = (AdvancedMessaging.objects.values('created').get(pk = request.POST.get('message_id')))['created']
                    messageid = request.POST.get('message_id')                    
            except ValueError:
                created_time = None
                messageid = 0
                
            token = request.POST.get("msgtoken")
            pkl_loc = _untokenize(token)
            with open(pkl_loc, 'rb') as f:
                my_adv_form = pickle.load(f)
            # send message to queue table
            
            if my_adv_form[0].cleaned_data.get('repeat_frequency') != "norepeat":
                message_reoccurs = True
                #next_delivery_time = get_next_delivery_time(my_adv_form[0].cleaned_data.get('repeat_frequency'),\
                #                                            my_adv_form[0].cleaned_data.get('delivery_time'))
                
                # the first (next) delivery time is the start time                
                next_delivery_time = my_adv_form[0].cleaned_data.get('delivery_time')
                repeat_until = time_to_utc(my_adv_form[0].cleaned_data.get('repeat_until'))
            else:
                message_reoccurs = False
                next_delivery_time = my_adv_form[0].cleaned_data.get('delivery_time')
                repeat_until = None
                
            fdt = (time_to_utc(my_adv_form[0].cleaned_data.get('delivery_time'))).strftime('%d-%m-%Y %H:%M')
            
            QueuedMessages.objects.create(
                message_type = request.POST.get("message_type"),
                message_id = messageid, #0 means it was never saved to draft
                message = {
                    'message_id' : messageid,
                    'title': my_adv_form[2].title, #myform.cleaned_data.get('title',''),
                    'email_template': my_adv_form[2].email_template,
                    'sms_template': my_adv_form[2].sms_template,
                    'send_email' : my_adv_form[2].send_email,
                    'send_sms' : my_adv_form[2].send_sms,
                    'sms_insert_optout' : my_adv_form[2].insert_optout,
                    'sms_sender_id' : my_adv_form[2].sms_sender,
                    'recipients' : my_adv_form[1], #request.POST.getlist('recipients',[]),
                    'smtp_setting_id': getattr(my_adv_form[2].smtp_setting, 'pk',''), #request.POST.get('smtp_setting','')
                    'others' : {
                                'draft_title' : my_adv_form[0].cleaned_data.get('title'),
                                'template_id' : my_adv_form[0].cleaned_data.get('message_template').id,
                                'original_created' : created_time.strftime('%d-%m-%Y %H:%M') if created_time else None,
                                'repeat_frequency' : my_adv_form[0].cleaned_data.get('repeat_frequency'),
                                'repeat_until' :  None if not repeat_until else repeat_until.strftime('%d-%m-%Y %H:%M'),
                                'first_delivery_time' : fdt,
                                'custom_data_namespace' : getattr(my_adv_form[0].cleaned_data.get('custom_data_namespace'),'namespace', None),
                                }
                           },
                recurring = message_reoccurs,
                delivery_time = next_delivery_time,
                created_by = request.user.kituser           
            )
            return {'result':'Success! Message Queued for Sending'}

def is_date_valid(date_text):
    try:
        dateutil.parser.parse(date_text)
        return [True, 'OK']
    except ValueError as e:
        return [False, e]
    except:
        e = (sys.exc_info())[1]
        return [False, e]
    '''
    try:
        if date_text != datetime.datetime.strptime(date_text, '%d/%m/%Y').strftime('%d/%m/%Y'):
            raise ValueError("Incorrect data format, should be DD/MM/YYYY")
        return True
    except ValueError:
        return False
    '''

def return_all_level_err(message):
    return json.dumps({'__all__': [{'message' : message}]})


def get_last_event_date(reminders, contact_dsoi):
    
    intdates = set()
    
    for reminder in reminders:
        for dsoi in contact_dsoi:
            ed = event_date(reminder[1],reminder[0],dsoi[1],reminder[2])
            intdates.add(ed)
    return max(intdates)
            
    


@ajax
@login_required
def run_reminder(request):
    
    if request.method == "POST":
        
        rmform = ReminderMessagingForm(request.POST)
        rm_formset = ReminderFormSet(request.POST)
        
        if not rmform.is_valid():
            return {'errors': rmform.errors.as_json(escape_html=True)}
        if not rm_formset.is_valid():
            return {'errors': return_all_level_err(rm_formset.non_form_errors())} #
        else:            
            try:
                #delete item from draft
                if ReminderMessaging.objects.filter(pk = request.POST.get('message_id')).exists():
                    messageid = request.POST.get('message_id')                
            except ValueError:
                messageid = 0
            
            # {"contact_id":"date_field"}
            data_result = CustomData.objects.values('data','data_table',\
                                'identity_column_name').get(pk=rmform.cleaned_data.get('custom_data_namespace'))
                                
            # convert data_table from customdata into a dataset for easy column selection
            dataset = tablib.Dataset()
            dataset.dict = data_result['data_table']
            
            # check that it is dates that are in the "date" column
            for item in dataset[rmform.cleaned_data.get('date_column')]:
                
                if is_date_valid(item)[0] is False:
                    return {'errors': return_all_level_err('Error encountered while validating the date column: '+\
                                                           str(is_date_valid(item)[1]))}
                    break
                
            recipient_group = request.POST.getlist('contact_group',[])
            grps = ContactGroup.objects.filter(pk__in = recipient_group).prefetch_related('contacts')
            contacts_id = set()
            
            for grp in grps:
                for contacts_per_group in grp.contacts.all():
                    contacts_id.add(contacts_per_group.pk)
            del grps #free memory, maybe
            

            
            # select the 'contacts' column
            contacts_column = dataset[data_result['identity_column_name']] #
            
            # get an intersection of contacts from the selected contact groups
            # and contacts from the uploaded customdata
            # The final contacts are less those contacts that strictly are not existing in the custom data
            # and not existing in the (expanded) contact groups.
            gogo_contacts = contacts_id.intersection(set(contacts_column))

            if gogo_contacts is None:
                return {'errors':return_all_level_err('It seems you have selected the wrong table column. We could not match any contact')}
            
            # get {contact_id:date}
            cdsoi = set()
            for recipient in gogo_contacts:
                cdsoi.add((recipient,data_result['data'][recipient][rmform.cleaned_data.get('date_column')]))
                
            print(cdsoi)
                
            rmdrs = set()
            for form in rm_formset:
                cd = form.cleaned_data
                if cd.get('delta_value') is None:
                    continue
                rmdrs.add((cd.get('delta_value'), cd.get('delta_type'), cd.get('delta_direction')))
            
            furthermost_event = get_last_event_date(rmdrs, cdsoi)    

            RunningMessage.objects.create(
                message = {
                    'message_id' : messageid,
                    'title': getattr(rmform.cleaned_data.get('message_template'), 'title', ''), #myform.cleaned_data.get('title',''),
                    'email_template': getattr(rmform.cleaned_data.get('message_template'), 'email_template',''),
                    'sms_template': getattr(rmform.cleaned_data.get('message_template'), 'sms_template',''),
                    'send_email' : getattr(rmform.cleaned_data.get('message_template'), 'send_email', ''),
                    'send_sms' : getattr(rmform.cleaned_data.get('message_template'), 'send_sms', ''),
                    'sms_sender_id' : getattr(rmform.cleaned_data.get('message_template'), 'sms_sender', ''),
                    'smtp_setting_id': getattr(rmform.cleaned_data.get('message_template'), 'smtp_setting.id',''),
                    'others' : {
                        'draft_title' : rmform.cleaned_data.get('title'),
                        'template_id' : rmform.cleaned_data.get('message_template').id,
                        'custom_data_namespace' : rmform.cleaned_data.get('custom_data_namespace').pk,
                        'date_column' : rmform.cleaned_data.get('date_column')                
                                }
                           },
                contact_dsoi = list(cdsoi),
                reminders = list(rmdrs),
                last_event_on = furthermost_event,
                created_by = request.user.kituser 
                                          )
            
              
            return {'result':'Reminder Started Successfully'}
        
        


@ajax
@login_required
def submit_issue_fb(request):
    
    if request.method == "POST":
        
        form = IssueFeedbackForm(request.POST, request.FILES)
        if not form.is_valid():
            return {'errors':form.errors.as_json(escape_html=True)}
        else:
            obj = form.save(commit=False)
            obj.submitter = request.user.kituser
            obj.save()
            return {'result':'Feedback Received.<br />Thank You'}