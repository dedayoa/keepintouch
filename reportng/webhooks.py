'''
Created on Sep 14, 2016

@author: Dayo
'''

import logging

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http.response import HttpResponse

from django.conf import settings

import json, copy
from .models import SMSDeliveryReportTransaction, CallDetailReportTransaction
from django.db.utils import IntegrityError


logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def infobip_sms_delivery_report_callback(request):
    data = request.body.decode('utf-8')
    meta = copy.copy(request.META)
    jdata = json.loads(data)
    
    for k, v in meta.copy().items():
        if not isinstance(v, str):
            del meta[k]
    
    SMSDeliveryReportTransaction.objects.create(body = jdata, request_meta = meta)
    
    return HttpResponse(status=200)



@csrf_exempt
@require_POST
def fs_call_detail_report_callback(request):
    calluid = request.GET.get('uuid')
    data = request.POST.get('cdr')
    meta = copy.copy(request.META)
    jdata = json.loads(data)
    
    for k, v in meta.copy().items():
        if not isinstance(v, str):
            del meta[k]
    
    # crazy sip spammers are flooding my FS server. I can't use a firewall (because app is on heroku -wtout public ip)
    # at the same time I want things to be as fast as possible, so no key/id comparisions - even from memory
    # so if the sender tries to duplicate the uuid and cause those massive errors I'm seeing, just ignore, but tell him
    # all went well. That's a bandwidth hog though so I need to figure out how to block them at source
    try:
        CallDetailReportTransaction.objects.create(call_uuid = calluid, body = jdata, request_meta = meta)
    except IntegrityError:
        logger.error('** Duplicate UUID: {} was sent'.format(calluid))
        return HttpResponse(status=200)
    
    return HttpResponse(status=200)