from django.shortcuts import render
from django.views.generic import UpdateView, CreateView

from .models import KITSystem
from .forms import SystemSettingsForm


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
