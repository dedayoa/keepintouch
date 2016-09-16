'''
Created on Sep 14, 2016

@author: Dayo
'''
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http.response import HttpResponse

from django.conf import settings

import json, copy
from .models import SMSDeliveryReportTransaction


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