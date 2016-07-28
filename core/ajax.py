#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.files.storage import default_storage
from django.db import transaction, IntegrityError
from django.core.files.base import ContentFile, File
from django.conf import settings

import psutil
import json
import datetime
import humanize
import base64
from cryptography.fernet import Fernet

from .models import KITUser, SMSTransfer, StateMaintainCache
from .forms import SMSTransferForm, ContactImportForm
from .impexp import ContactResource
import tablib
import sys
import os
import uuid
from core.models import UploadedContact

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
        result_dict['total_sms_balance'] = request.user.kituser.sms_balance 
        
        print(request.user.kituser.get_queued_messages())
        
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
                user = KITUser.objects.select_for_update().get(id=user.id)
                admin = KITUser.objects.select_for_update().get(id=request.user.kituser.id)
                              
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
                                from_user = admin,
                                to_user = user,
                                sms_units = amount,
                                transaction_detail = {
                                        'from_user_email' : admin.user.email,
                                        'to_user_email' : user.user.email
                                                      },
                                created_by = admin
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
                            from_user = user,
                            to_user = admin,
                            sms_units = amount,
                            transaction_detail = {
                                    'from_user_email' : user.user.email,
                                    'to_user_email' : admin.user.email
                                                  },
                            created_by = admin
                        )
                    
                result_dict['user_sms_bal'] = user.sms_balance
                result_dict ['admin_sms_bal'] = admin.sms_balance
                
            except IntegrityError:
                print("Integrity Error Occured")
                
            return {'result': result_dict}
        
        

@ajax
@login_required
def get_user_sms_balance(request):
    
    if request.method == "GET":
        result_dict = {}
        ku = KITUser.objects.get(pk=request.GET.get("users"))
        result_dict["user_sms_bal"] = ku.sms_balance 
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
        print(file)
        if (fext[1:]).lower() == 'csv':
            dataset = tablib.Dataset().load(open(file,'r').read(), format="csv")
        else:
            dataset = tablib.Dataset().load(open(file,'rb').read(), format="xls")
        
        dataset.append_col(lambda row: kuserid,'kit_user')
        
        res_cr_dr = cr.import_data(dataset, dry_run=False)
        
        if res_cr_dr.has_errors():
            return 'err21' #error occured during dry run
        else:
            return res_cr_dr.totals
            
    except:
        print(sys.exc_info())#[0])    
        
        
@ajax
@login_required
@transaction.atomic
def now_import_contacts(request):
    
    if request.method == 'POST':
                   
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
                file = File(open(file_loc, 'rb')),
                import_status = result,
                uploaded_by = request.user.kituser
                )
        
        return {'result':'Done!'}
        