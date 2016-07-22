
from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import transaction, IntegrityError

import psutil
import json
import datetime
import humanize

from .models import KITUser, SMSTransfer
from .forms import SMSTransferForm

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
        result_dict['pmc'] = request.user.kituser.get_queued_messages().count()
        result_dict['qmc'] = request.user.kituser.get_processed_messages().count()
        
        return {'result': result_dict}
    
    
@ajax
@login_required
@transaction.atomic
def sms_credit_transfer(request):
    
    
    if request.method == "POST":
        print("Hello")
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