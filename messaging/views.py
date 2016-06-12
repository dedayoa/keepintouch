from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _, ugettext

from django_tables2   import RequestConfig

from .models import StandardMessaging, AdvancedMessaging
from core.models import KITUser 
from .forms import StandardMessagingForm, AdvancedMessagingForm
from .tables import *
from django.http.response import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse

# Create your views here.

def messaging_standard(request):
    
    if request.method == "GET":
        q_user = KITUser.objects.get(user=request.user)
        #q_grps = q_user.group.all() #groups the user belongs to
        #q_publ_ev = PublicEvent.objects.filter(event_group__in=q_grps)

        #s_message_table = PublicEventTable(q_user.get_public_events())
        #RequestConfig(request, paginate={'per_page': 25}).configure(s_message_table)
        params = {}
        params["title"] = "Standard Messages"
        #params["table"] = s_message_table
        return render(request, 'core/events/public_events_index.html', params)

def messaging_by_status(request):
    
    return HttpResponse()


class StandardMessageCreateView(CreateView):
    
    model = StandardMessaging
    form_class = StandardMessagingForm
    template_name = 'messaging/standard/new_standard_message.html'
    #success_url = reverse_lazy('messaging:new-standard-message')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user.kituser

        return super(StandardMessageCreateView, self).form_valid(form)
    
    def get_context_data(self, **kwargs):
        self.params = super(StandardMessageCreateView, self).get_context_data(**kwargs)
        self.params["title"] = _("Create Standard Message")        
        return self.params
    
    def get_success_url(self):
        return reverse('messaging:standard-message-draft', kwargs={'pk': self.object.pk})
    
    
class StandardMessageUpdateDraftView(UpdateView):
    
    model = StandardMessaging
    form_class = StandardMessagingForm
    template_name = 'messaging/standard/standard_message_draft.html'
    
    
    def get_context_data(self, **kwargs):
        params = super(StandardMessageUpdateDraftView, self).get_context_data(**kwargs)
        params["title"] = _("Message")
        params["draft_time"] = self.object.last_modified
        params["messageid"] = self.object.pk  
        
        return params
    
    def get_object(self, queryset=None):
        return self.model.objects.get(status="draft", created_by=self.request.user.kituser)
        
    
    
class AdvancedMessageCreateView(CreateView):
    
    model = AdvancedMessaging
    form_class = AdvancedMessagingForm
    template_name = 'messaging/advanced/new_advanced_message.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user.kituser

        return super(AdvancedMessageCreateView, self).form_valid(form)
    
    def get_context_data(self, **kwargs):
        self.params = super(AdvancedMessageCreateView, self).get_context_data(**kwargs)
        self.params["title"] = _("Create Advanced Message")        
        return self.params
    
    def get_success_url(self):
        return reverse('messaging:advanced-message-draft', kwargs={'pk': self.object.pk})
    

class AdvancedMessageUpdateDraftView(UpdateView):
    
    model = AdvancedMessaging
    form_class = AdvancedMessagingForm
    template_name = 'messaging/advanced/advanced_message_draft.html'
    
    
    def get_context_data(self, **kwargs):
        params = super(AdvancedMessageUpdateDraftView, self).get_context_data(**kwargs)
        params["title"] = _("Advanced Message")
        params["draft_time"] = self.object.last_modified
        params["messageid"] = self.object.pk       
        return params
    
    def get_object(self, queryset=None):
        return self.model.objects.get(status="draft", created_by=self.request.user.kituser)
    
class StandardMessageDeleteView(DeleteView):
    
    model = StandardMessaging
    success_url = reverse_lazy('messaging:new-standard-message')
    
    def get_context_data(self, **kwargs):
        params = super(StandardMessageDeleteView, self).get_context_data(**kwargs)
        params["title"] = "Deleting Message"
        return params
    

class AdvancedMessageDeleteView(DeleteView):
    
    model = AdvancedMessaging
    success_url = reverse_lazy('messaging:new-advanced-message')
    
    def get_context_data(self, **kwargs):
        params = super(AdvancedMessageDeleteView, self).get_context_data(**kwargs)
        params["title"] = "Deleting Message"
        return params
    
    
def message_status_view(request, msgstat):
    
    if request.method == "GET":
        if msgstat == "draft":
            return HttpResponse("Draft")
        
    