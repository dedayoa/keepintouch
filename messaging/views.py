from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _, ugettext

from django_tables2   import RequestConfig

from .models import StandardMessaging
from core.models import KITUser 
from .forms import StandardMessagingForm
from .tables import *
from django.http.response import HttpResponse
from django.views.generic.edit import CreateView, UpdateView
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

def messaging_advanced(request):
    
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
        
        return params
        
    
    
class AdvancedMessageCreateView(CreateView):
    
    model = StandardMessaging
    form_class = StandardMessagingForm
    template_name = 'messaging/standard/new_standard_message.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user.kituser

        return super(StandardMessageCreateView, self).form_valid(form)
    
