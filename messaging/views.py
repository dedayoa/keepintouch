from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _, ugettext

from django_tables2   import RequestConfig

from .models import StandardMessaging, AdvancedMessaging, ProcessedMessages,\
                    QueuedMessages
from core.models import KITUser
 
from .forms import StandardMessagingForm, AdvancedMessagingForm
from .tables import DraftStandardMessagesTable, DraftAdvancedMessagesTable, ProcessedMessagesTable,\
                    QueuedMessagesTable
from .filters import ProcessedMessagesFilter

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
    
    def get_form_kwargs(self):
        kwargs = super(StandardMessageCreateView, self).get_form_kwargs()
        kwargs.update({'kituser': self.request.user.kituser})
        return kwargs
    
    
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
        return self.model.objects.get(pk=self.kwargs.get('pk',None),status="draft", created_by=self.request.user.kituser)


    def get_form_kwargs(self):
        kwargs = super(StandardMessageUpdateDraftView, self).get_form_kwargs()
        kwargs.update({'kituser': self.request.user.kituser})
        return kwargs
    
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
    
    ##??  You could set the field here or using get_form_kwargs  as above ??##
    def get_form(self, form_class=form_class):
        form = super(AdvancedMessageCreateView, self).get_form(form_class)
        form.fields["message_template"].queryset = self.request.user.kituser.get_templates()
        form.fields['contact_group'].queryset = self.request.user.kituser.get_contact_groups()
        
        return form
    
    def get_success_url(self):
        return reverse('messaging:advanced-message-draft', kwargs={'pk': self.object.pk})

    

class AdvancedMessageUpdateDraftView(UpdateView):
    
    model = AdvancedMessaging
    form_class = AdvancedMessagingForm
    template_name = 'messaging/advanced/advanced_message_draft.html'
    
    def get_form(self, form_class=form_class):
        form = super(AdvancedMessageUpdateDraftView, self).get_form(form_class)
        form.fields["message_template"].queryset = self.request.user.kituser.get_templates()        
        return form
        
    
    def get_context_data(self, **kwargs):
        params = super(AdvancedMessageUpdateDraftView, self).get_context_data(**kwargs)
        params["title"] = _("Advanced Message")
        params["draft_time"] = self.object.last_modified
        params["messageid"] = self.object.pk
        return params
    
    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs.get('pk',None),status="draft", created_by=self.request.user.kituser)
    
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
    
    
def standard_message_draft_view(request):
    
    if request.method == "GET":
        query = StandardMessaging.objects.filter(status="draft", created_by=request.user.kituser)
        draft_msgs_table = DraftStandardMessagesTable(query)
        RequestConfig(request, paginate={'per_page': 25}).configure(draft_msgs_table)
        params = {}
        params["title"] = "Draft Messages"
        params["table"] = draft_msgs_table
        return render(request, 'messaging/standard/draft_standard_messages_list.html', params)
        
        
def advanced_message_draft_view(request):
    
    if request.method == "GET":
        query = AdvancedMessaging.objects.filter(status="draft", created_by=request.user.kituser)
        draft_msgs_table = DraftAdvancedMessagesTable(query)
        RequestConfig(request, paginate={'per_page': 25}).configure(draft_msgs_table)
        params = {}
        params["title"] = "Draft Messages"
        params["table"] = draft_msgs_table
        return render(request, 'messaging/advanced/draft_advanced_messages_list.html', params)
        
def message_processed_status_view(request):
    
    if request.method == "GET":
        
        queryset = request.user.kituser.get_processed_messages()#ProcessedMessages.objects.filter(created_by=request.user.kituser)
        f = ProcessedMessagesFilter(request.GET, \
                                    queryset=queryset)
        p_msgs_table = ProcessedMessagesTable(f.qs)
        RequestConfig(request, paginate={'per_page': 50}).configure(p_msgs_table)
        params = {}
        params["title"] = "Processed Messages"
        params["table"] = p_msgs_table
        params["filter"] = f
        return render(request, 'messaging/processed_messages.html', params)
    
    
def message_queued_status_view(request):
    
    if request.method == "GET":
        
        queryset = request.user.kituser.get_queued_messages()#QueuedMessages.objects.filter(created_by=request.user.kituser)
        q_msgs_table = QueuedMessagesTable(queryset, order_by="delivery_time")
        RequestConfig(request, paginate={'per_page': 50}).configure(q_msgs_table)
        params = {}
        
        params["title"] = "Queued Messages"
        params["table"] = q_msgs_table
        return render(request, 'messaging/queued_messages.html', params)
    
    
def queued_message_dequeue_view(request, mtype, pk):
    
    if request.method == "POST":
        if mtype == "ADVANCED":
            return HttpResponse("Advanced")
        elif mtype == "STANDARD":
            return HttpResponse("Standard")
    