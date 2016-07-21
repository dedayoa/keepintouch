
from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax
from django.contrib.humanize.templatetags.humanize import naturaltime

import psutil
import datetime
import humanize

from .models import KITUser

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