
import mimetypes

from django.shortcuts import render
from django.views.generic import UpdateView, CreateView, TemplateView
from django.conf import settings

from django_tables2 import RequestConfig

from .models import KITSystem, CustomData
from .forms import SystemSettingsForm, CustomDataIngestForm
from .tables import CustomDataStoreTable


def smslive247_callback():
    pass
    
    
class SystemSettingsUpdateView(UpdateView):
    
    model = KITSystem
    form_class = SystemSettingsForm
    template_name = 'gomez/system_settings.html'
    
    def get_context_data(self, **kwargs):
        params = super(SystemSettingsUpdateView, self).get_context_data(**kwargs)
        params["syssetid"] = self.object.pk
        return params



class CustomDataView(TemplateView):
    
    template_name = 'gomez/data_mgmt/custom_data.html'
    params = {}
    ingest_form = CustomDataIngestForm()
    
    def get(self, request):
        self.params["ingest_form"] = self.ingest_form
        self.params['file_max_size'] = settings.MAX_UPLOAD_FILE_SIZE
        self.params["title"] = "Custom Data Management"
                
        custdatable = CustomDataStoreTable(CustomData.objects.filter(created_by = request.user.kituser).order_by('-created'))
        RequestConfig(request, paginate={'per_page': 30}).configure(custdatable)
        self.params["table"] = custdatable
        
        
        return render(request, self.template_name, self.params)
