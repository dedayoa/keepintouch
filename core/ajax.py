#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.files.storage import default_storage
from django.db import transaction, IntegrityError
from django.core.files.base import ContentFile, File
from django.conf import settings
from django.contrib import messages as flash_messages

import psutil
import json
import datetime
import humanize
import base64
from cryptography.fernet import Fernet

from .models import KITUser, SMSTransfer, CustomData, Contact, KITUBalance, KITActivationCode,\
                    OrganizationContact
from .forms import SMSTransferForm, ContactImportForm, CustomDataIngestForm, VerifyAccountForm,\
                    OrganizationContactForm
from .impexp import ContactResource
import tablib
import sys
import os
import uuid
import logging
from core.models import UploadedContact
from django.utils.text import slugify
from tablib.core import UnsupportedFormat
from django.http.response import HttpResponseRedirect
from django.utils import timezone

from ipware.ip import get_real_ip


logger = logging.getLogger(__name__)

@ajax
@login_required
def get_system_stats(request):
    
    if request.method == "GET":
        result_dict = {}
        result_dict['cpu'] = psutil.cpu_percent(interval=None)
        result_dict['ram'] = "{}/{}".format(humanize.naturalsize(psutil.virtual_memory().used, binary=True),\
                                            humanize.naturalsize(psutil.virtual_memory().total, binary=True))
        result_dict['disk_usage'] = psutil.disk_usage('/').percent
        result_dict['uptime'] = naturaltime(datetime.datetime.fromtimestamp(psutil.boot_time()))
        
        return {'result': result_dict}
    
    
@ajax
@login_required
def get_qpc_stats(request):
    
    if request.method == "GET":
        
        #q_user = KITUser.objects.get(user=request.user)
        result_dict = {}
        result_dict['qmc'] = request.user.kituser.get_queued_messages().count()
        result_dict['pmc'] = request.user.kituser.get_processed_messages().count()
        result_dict['total_sms_balance'] = request.user.kituser.kitubalance.sms_balance
        result_dict['free_sms_balance'] = request.user.kituser.kitubalance.free_sms_balance
        
        return {'result': result_dict}
    

def return_all_level_err(message):
    return json.dumps({'__all__': [{'message' : message}]}
                                            )

    
@ajax
@login_required
@transaction.atomic
def sms_credit_transfer(request):
    
    
    if request.method == "POST":
        result_dict = {}
        myform = SMSTransferForm(request.POST, crequest=request)
        if not myform.is_valid():
            return {'errors':myform.errors.as_json(escape_html=True)}
        else:
                
            amount = myform.cleaned_data.get("amount")
            user = myform.cleaned_data.get("users")
            try:
                #user = KITUser.objects.select_for_update().get(id=user.id)
                #admin = KITUser.objects.select_for_update().get(id=request.user.kituser.id)
                
                user = KITUBalance.objects.select_for_update().get(kit_user=user.id)
                admin = KITUBalance.objects.select_for_update().get(kit_user=request.user.kituser.id)
                              
                if request.POST.get("mdir") == 'credit': #give user units
                    #check before db entry that admin has sufficient balance to execute the transaction
                    
                    rek = admin.sms_balance - amount
                    if rek <= 0:
                        return {'errors': json.dumps(
                                                {'__all__': [{'message' : 'Admin does not have enough balance to complete transaction'}]}
                                            )
                                    }
                    else:
                        
                            user.sms_balance = user.sms_balance + amount
                            admin.sms_balance = admin.sms_balance - amount
                            user.save()
                            admin.save()
                            SMSTransfer.objects.create(
                                from_user = admin.kit_user,
                                to_user = user.kit_user,
                                sms_units = amount,
                                transaction_detail = {
                                        'from_user_email' : admin.kit_user.user.email,
                                        'to_user_email' : user.kit_user.user.email
                                                      },
                                created_by = admin.kit_user
                            )
                elif request.POST.get("mdir") == 'debit':
                    
                    uek = user.sms_balance - amount 
                    if uek <= 0:
                        return {'errors': json.dumps(
                                                {'__all__': [{'message' : 'User does not have enough balance to complete transaction'}]}
                                            )
                                    }
                    else:    
                        user.sms_balance = user.sms_balance - amount
                        admin.sms_balance = admin.sms_balance + amount
                        user.save()
                        admin.save()
                        SMSTransfer.objects.create(
                            from_user = user.kit_user,
                            to_user = admin.kit_user,
                            sms_units = amount,
                            transaction_detail = {
                                    'from_user_email' : user.kit_user.user.email,
                                    'to_user_email' : admin.kit_user.user.email
                                                  },
                            created_by = admin.kit_user
                        )
                    
                result_dict['user_sms_bal'] = user.sms_balance
                result_dict['admin_sms_bal'] = admin.sms_balance
                
            except IntegrityError:
                print("Integrity Error Occured")
                
            return {'result': result_dict}
        
        

@ajax
@login_required
def get_user_sms_balance(request):
    
    if request.method == "GET":
        result_dict = {}
        ku = KITUser.objects.select_related('kitubalance').get(pk=request.GET.get("users"))
        result_dict["user_sms_bal"] = ku.kitubalance.sms_balance
        return {'result': result_dict}



def _salutation_to_lower_case(ds):
    nu_r = tablib.Dataset()
    nu_r.headers = ds.headers
    while len(ds) > 0:
        r = ds.lpop()
        nu_r.append((r[0].lower(), r[1], r[2], r[3], r[4]))
    return nu_r

def dry_run_file(file, fext, kuserid):
    
    try:
        #print(file.read())
        cr = ContactResource()
        #read_file = file.read()
        #read_dec_file = read_file.decode() 
        if (fext[1:]).lower() == 'csv':
            dataset = tablib.Dataset().load(open(file,'r').read())
        else:
            dataset = tablib.Dataset().load(open(file,'rb').read())
        #check that headers 
        fhdr = ['salutation','first_name','last_name','phone','email']
        if dataset.headers is None:
            dataset.headers = fhdr
        if set(fhdr) != set(dataset.headers):
            return 'err10' #header is something else!
        else:
            clean_ds = _salutation_to_lower_case(dataset)
            
            clean_ds.append_col(lambda row: kuserid,'kit_user')
            
            res_cr_dr = cr.import_data(clean_ds, dry_run=True)
            
            if res_cr_dr.has_errors():
                return 'err21' #error occured during dry run
            else:
                #StateMaintainCache.objects.create(obj=read_file)
                del clean_ds['kit_user']
                return [clean_ds.json, res_cr_dr.totals]
            
    except:
        print(sys.exc_info())#[0])
        

def get_upfile_handle(upfile):
    
    with open(upfile.name,'wb+') as infile:
        for chunk in upfile.chunks():
            infile.write(chunk)
    return infile
    

@ajax
@login_required
def get_contact_file_upload(request):
    
    if request.method == "POST":
        
        result_dict = {}
        
        form = ContactImportForm(request.POST, request.FILES)
        if form.is_valid():
            upinfile = request.FILES.get('file')
            fext = os.path.splitext(str(upinfile))[1]
            file_path = os.path.join(settings.MEDIA_ROOT, 'tmp/'+str(uuid.uuid4())+fext)
            upfile_path = default_storage.save(file_path, ContentFile(upinfile.read()))
            
            aix = bytes(settings.SECRET_KEY[:32],'utf-8')
            f = Fernet(base64.urlsafe_b64encode(aix))
            token = f.encrypt(bytes(upfile_path,'utf-8'))
            
            dr_resp = dry_run_file(upfile_path, fext, request.user.kituser.id)
            if dr_resp == 'err10':
                return {'errors': return_all_level_err(dr_resp)}
            elif dr_resp == 'err21':
                return {'errors': return_all_level_err(dr_resp)}
            else:
                return {'result': {'jsont':dr_resp[0],'opdet':dr_resp[1], 'namega': form.cleaned_data.get('name'),'sook':token.decode('utf-8')}}
        else:
            return {'errors': form.errors.as_json()}


def wet_run_file(file, fext, kuserid):
    
    try:
        #print(file.read())
        cr = ContactResource()
        #read_file = file.read()
        #read_dec_file = read_file.decode()
        if (fext[1:]).lower() == 'csv':
            with open(file, 'r') as f:                
                dataset = tablib.Dataset().load(f.read(), format="csv")
        else:
            with open(file,'rb') as f:
                dataset = tablib.Dataset().load(f.read(), format="xls")
        dataset_ut = dataset.dict
        dataset.append_col(lambda row: kuserid,'kit_user')
        
        res_cr_dr = cr.import_data(dataset, dry_run=False)
        
        if res_cr_dr.has_errors():
            return 'err21' #error occured during wet run
        else:
            return [res_cr_dr.totals, dataset_ut] 
            
    except:
        print(sys.exc_info())#[0])    
        
        
@ajax
@login_required
@transaction.atomic
def now_import_contacts(request):
    
    if request.method == 'POST':
                   
        try:
            file_name = request.POST.get('namega')
            enc_file_loc = request.POST.get('sook')
        
            aix = bytes(settings.SECRET_KEY[:32],'utf-8')
            f = Fernet(base64.urlsafe_b64encode(aix))
            file_loc = (f.decrypt(bytes(enc_file_loc,'utf-8'))).decode('utf-8')
            
            fext = os.path.splitext(str(file_loc))[1]
            
            result = wet_run_file(file_loc, fext, request.user.kituser.id)
            
            #save upload to the uploaded table
            UploadedContact.objects.create(
                    name = file_name,
                    #file = File(open(file_loc, 'rb')),
                    file_json = result[1],
                    file_extension = fext[1:], #remove leading dot
                    import_status = result[0],
                    uploaded_by = request.user.kituser
                    )            
            return {'result':'Done!'}
        except:
            print(sys.exc_info())
            return {'result':'Error Occured! Please Try Again'}



########################################



def us_slugify(value, seperator='-'):
    return slugify(value).replace('-', seperator)

def clean_header(header):
    d_hdrs = []
    x = 1
    for item in header:
        if item in d_hdrs:
            item = str(item)+"_"+x
        d_hdrs.append(us_slugify(item, '_'))
        x+=1
    return d_hdrs       
        
@ajax
@login_required        
def upload_custom_data(request):
    

    
    if request.method == "POST":
        
        form = CustomDataIngestForm(request.POST, request.FILES)
        
        if not form.is_valid():
            return {'errors': form.errors.as_json()}
        else:
            result_dict = {}
            
            upinfile = request.FILES.get('file')
            uqf_ptr = request.POST.get('unique_field')
            
            try:
                idata_headers = tablib.Dataset().load(upinfile.read()).headers
                #idata_headers[:] = [us_slugify(s, '_') for s in idata_headers]
                
                result_dict['idata_headers'] = clean_header(idata_headers)
                
                upinfile.seek(0)
                
                fext = os.path.splitext(str(upinfile))[1]
                file_path = os.path.join(settings.MEDIA_ROOT, 'tmp/'+str(uuid.uuid4())+fext)
                upfile_path = default_storage.save(file_path, ContentFile(upinfile.read()))
                
                aix = bytes(settings.SECRET_KEY[:32],'utf-8')
                f = Fernet(base64.urlsafe_b64encode(aix))
                token = f.encrypt(bytes(upfile_path,'utf-8'))
                
                result_dict['token'] = token
                result_dict['unqf_idfr'] = uqf_ptr
                
                return {"result" : result_dict}
            except KeyError:
                return {'errors' : return_all_level_err(str(sys.exc_info()[1]))}
            except UnsupportedFormat:
                return {'errors' : return_all_level_err('A file with Unsupported table format was uploaded')}



@ajax
@login_required
def process_1_custom_data(request):
    
    if request.method == "POST":
        enc_file_loc = request.POST.get("token")
        id_fld_ptr = request.POST.get("identity_fld_ptr")
        unqf_idfr = request.POST.get("unqf_idfr")
        
        aix = bytes(settings.SECRET_KEY[:32],'utf-8')
        f = Fernet(base64.urlsafe_b64encode(aix))
        file_loc = (f.decrypt(bytes(enc_file_loc,'utf-8'))).decode('utf-8')
        fext = os.path.splitext(str(file_loc))[1]
        '''
        'owner': {
            'name': 'Bob',
            'other_pets': 'Fishy'
        },
        'owner2': {
            'name': 'Tim',
            'other_pets': 'Crabby'
        },
        '''
        def process_data(ds_in_dict, identity_column_name, unqfid):
            #converts a standard ds.dict into more accessible json
            # also ensure the key is always contact ID
            new_dict = {}
            new_inner_dict = {}
            for row in ds_in_dict:
                for k,v in row.items():
                    if unqfid == "coid":
                        if k==identity_column_name:
                            new_dict[v] = new_inner_dict
                        else:
                            new_inner_dict[k] = v
                    elif unqfid == "doid":
                        if k==identity_column_name:
                            try:
                                ctct = Contact.objects.get(domain_id=v)
                                new_dict[ctct.pk] = new_inner_dict
                            except Contact.DoesNotExist:
                                logger.error('While importing Custom Data, no ContactID match was found for the DomainID {}'.format(v))
                        else:
                            new_inner_dict[k] = v
                            
                new_inner_dict = {}
            return new_dict
        
        
        def process_dataset(ds):
            
            ds.headers[:] = clean_header(ds.headers)
            
            if unqf_idfr == "coid":
                t = CustomData.objects.create(
                    identity_column_name =  ds.headers[int(id_fld_ptr)],
                    system_id_field = unqf_idfr,
                    headers = ds.headers,
                    data = process_data(ds.dict, ds.headers[int(id_fld_ptr)], unqfid="coid"),
                    data_table = ds.dict,
                    created_by = request.user.kituser
                )
                return t
            elif unqf_idfr == "doid":
                t = CustomData.objects.create(
                    identity_column_name =  ds.headers[int(id_fld_ptr)],
                    system_id_field = unqf_idfr,
                    headers = ds.headers,
                    data = process_data(ds.dict, ds.headers[int(id_fld_ptr)], unqfid="doid"),
                    data_table = ds.dict,
                    created_by = request.user.kituser
                )
                return t
            
        
        
        if (fext[1:]).lower() == 'csv':
            with open(file_loc, 'r') as f:         
                dataset = tablib.Dataset().load(f.read(), format="csv")
                result = process_dataset(dataset)
            return {"result":result}
        else:
            with open(file_loc,'rb') as f:
                dataset = tablib.Dataset().load(f.read(), format="xls")
                result = process_dataset(dataset)
            return {"result":result}
            

@ajax
@login_required        
def get_custom_data_ajax(request, pk):
    
    if request.method == "GET":
        result_dict = {}
        custd = CustomData.objects.get(pk=pk)
        result_dict["data_table"] = custd.data_table
        result_dict["headers"] = custd.headers
        result_dict["identity_field"] = custd.system_id_field
        result_dict["id_key"] = custd.identity_column_name
        
        return {"result":result_dict}
        
@ajax
@login_required          
def delete_custom_data_ajax(request, pk):
    
    if request.method == "POST":
        result = CustomData.objects.get(pk=pk, created_by=request.user.kituser).delete()
        return {"result":result}
    
    

@ajax
@login_required
def get_custom_data_columns(request, pk=None):
    
    if request.method == "GET":
        # watch out, you may need to do (, created_by=request.user.kituser)
        if pk is None:
            return {'result':"nil"}
        hdrs = CustomData.objects.values("headers",'identity_column_name').get(pk=pk)

        hdrs['headers'].remove(hdrs['identity_column_name'])
        
        return {'result':hdrs['headers']}
    
    
@ajax
@login_required
def send_verification_code(request):
    if request.method == "POST":
        # expire every other unexpired code
        # create new verification
        # send email and phone number to verify...based on whether already verified
        form = VerifyAccountForm(request.POST, user=request.user)
        form_2 = OrganizationContactForm(request.POST)
        if not form.is_valid():
            return {'errors':form.errors.as_json(escape_html=True)}
        elif not form_2.is_valid():
            return {'errors':form_2.errors.as_json(escape_html=True)}
        else:
            # update User & KITUser with info received           
            user = request.user
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
            
            oc = form_2.save()
            
            kuser= request.user.kituser #previously used a select, resulted in a "miss" for every param until next request. BEWARE!
            kuser.ip_address = get_real_ip(request)
            kuser.dob = form.cleaned_data.get('date_of_birth')
            kuser.timezone = form.cleaned_data.get('timezone')
            kuser.phone_number = form.cleaned_data.get('phone_number')
            kuser.organization = form.cleaned_data.get('organization_name')
            kuser.industry = form.cleaned_data.get('industry')
            kuser.address = oc
            kuser.save()
            
            
            
            # delete existing activation keys for this user.
            KITActivationCode.objects.filter(user=request.user).delete()
            #create new activation key
            KITActivationCode.objects.create(user=request.user)
       
            return {'result','Verification Code Sent'}
    
    
@ajax
@login_required
def verify_user_details(request):
    if request.method == "POST":
        form = VerifyAccountForm(request.POST, user=request.user)
        if not form.is_valid():
            return {'errors':form.errors.as_json(escape_html=True)}
        else:
            activation_details = request.user.kitactivationcode
            if activation_details.expired:
                flash_messages.add_message(request, flash_messages.INFO,'Activation Codes Expired. Click "Send Code" button to generate a new set.')
                return HttpResponseRedirect('/')
            else:
                evc = form.cleaned_data.get('email_verification_code','')
                pvc = form.cleaned_data.get('phone_number_verification_code','')
                #  check if email is verified
                if request.user.kituser.email_validated == False:
                    if evc == activation_details.email_activation_code:
                        # update kituser
                        KITUser.objects.filter(user=request.user.id).update(
                                                email_validated = True,
                                                email_validated_date = timezone.now()
                                                )
                    else:
                        flash_messages.add_message(request, flash_messages.INFO, 'Invalid Email Verification Code. Kindly re-check or generate a new set')
                
                if request.user.kituser.phone_validated == False:
                    if pvc == activation_details.phone_activation_code:
                        if request.user.kituser.phone_number != form.cleaned_data.get('phone_number'):
                            flash_messages.add_message(request, flash_messages.INFO, 'To change your phone number, resend Verification Code again')
                            
                        else:
                            # update kituser
                            KITUser.objects.filter(user=request.user.id).update(
                                                    phone_validated = True,
                                                    phone_validated_date = timezone.now()
                                                                             )
                    else:
                        flash_messages.add_message(request, flash_messages.INFO, 'Invalid Phone Verification Code. Kindly re-check or generate a new set')
                return HttpResponseRedirect('/')
    