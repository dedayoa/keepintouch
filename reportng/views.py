
from django.shortcuts import render, get_object_or_404, render_to_response
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib import messages as flash_messages

from django.http.response import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView, View
from django.core.urlresolvers import reverse_lazy, reverse

from django.contrib.auth.mixins import PermissionRequiredMixin
# Create your views here.

from .models import SMSDeliveryReport

from .tables import SMSReportTable

from django.core.exceptions import ObjectDoesNotExist

from cacheops import cached_as
from django_tables2.config import RequestConfig


class SMSReport(View):
    
    template_name = 'reportng/sms_index.html'
    params= {}
    
    @cached_as(timeout=600)
    def get_xydata(self, request):
        status = dict(SMSDeliveryReport.STATUS)
        
        xdata = []
        ydata = []
        
        try:
            for k,v in status.items():
                xdata.append(v)
                if request.user.kituser.is_admin:
                    ydata.append(SMSDeliveryReport.objects.filter(kitu_parent_id=request.user.kituser.id, msg_status=k).count())
                else:
                    ydata.append(SMSDeliveryReport.objects.filter(kituser_id=request.user.kituser.id, msg_status=k).count())
            return [xdata, ydata]
        except ObjectDoesNotExist:
            return [0,0,0,0,0,0]
        
        
    
    def get(self, request):
        self.params['title'] = 'SMS Report'
        self.params['body_class'] = 'sms-report-page'
        
        xdata = self.get_xydata(request)[0]
        ydata = self.get_xydata(request)[1]
    
        extra_serie1 = {"tooltip": {"y_start": "", "y_end": " cal"}}
        chartdata = {
            'x': xdata, 'name1': '', 'y1': ydata, 'extra1': extra_serie1,
        }
        charttype = "discreteBarChart"
        chartcontainer = 'discretebarchart_container'  # container name
        self.params['data'] = {
            'charttype': charttype,
            'chartdata': chartdata,
            'chartcontainer': chartcontainer,
            'extra': {
                'x_is_date': False,
                'x_axis_format': '',
                'tag_script_js': True,
                'jquery_on_ready': True,
            },
        }
        
        if request.user.kituser.is_admin:
            reporttable = SMSReportTable(SMSDeliveryReport.objects.filter(kitu_parent_id=request.user.kituser.id).order_by('-created'))
        else:
            reporttable = SMSReportTable(SMSDeliveryReport.objects.filter(kituser_id=request.user.kituser.id).order_by('-created'))
        RequestConfig(request, paginate={'per_page': 25}).configure(reporttable)
        self.params["table"] = reporttable        
        
        return render(request, self.template_name, self.params)