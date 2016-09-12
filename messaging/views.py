from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib import messages as flash_messages

from django_tables2   import RequestConfig

from .models import StandardMessaging, AdvancedMessaging, ProcessedMessages,\
                    QueuedMessages, ReminderMessaging, Reminder, FailedEmailMessage, FailedSMSMessage,\
                    FailedKITMessage
from core.models import KITUser
 
from .forms import StandardMessagingForm, AdvancedMessagingForm, ReminderMessagingForm,\
                    ReminderFormSet
from .tables import DraftStandardMessagesTable, DraftAdvancedMessagesTable, ProcessedMessagesTable,\
                    QueuedMessagesTable, DraftReminderMessagesTable, RunningMessagesTable,\
                    FailedEmailMessagesTable, FailedSMSMessagesTable, FailedKITMessagesTable

### Admin Tables #####
from .tables import FailedSMSMessagesTable_Admin, FailedEmailMessagesTable_Admin


from .filters import ProcessedMessagesFilter

from .tasks import process_private_anniversary, process_onetime_event, process_public_anniversary,\
                    process_reminder_event, _send_sms, _send_email

from django.http.response import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from core.tables import ContactTable

from django.contrib.auth.mixins import PermissionRequiredMixin

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
        form.fields["message_template"].queryset = self.request.user.kituser.get_templates().filter(active=True)
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
        form.fields["message_template"].queryset = self.request.user.kituser.get_templates().filter(active=True)      
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

    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        qs = super(StandardMessageDeleteView, self).get_queryset(**kwargs)
        return qs.filter(created_by=self.request.user.kituser)
    

class AdvancedMessageDeleteView(DeleteView):
    
    model = AdvancedMessaging
    success_url = reverse_lazy('messaging:new-advanced-message')
    
    def get_context_data(self, **kwargs):
        params = super(AdvancedMessageDeleteView, self).get_context_data(**kwargs)
        params["title"] = "Deleting Message"
        return params
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        qs = super(AdvancedMessageDeleteView, self).get_queryset(**kwargs)
        return qs.filter(created_by=self.request.user.kituser)
    
    
def standard_message_draft_view(request):
    
    if request.method == "GET":
        query = StandardMessaging.objects.filter(status="draft", created_by=request.user.kituser)
        draft_msgs_table = DraftStandardMessagesTable(query)
        RequestConfig(request, paginate={'per_page': 25}).configure(draft_msgs_table)
        params = {}
        params["title"] = "Draft Messages"
        params["table"] = draft_msgs_table
        params["herpath"] = (request.path.split('/'))[2]
        return render(request, 'messaging/standard/draft_standard_messages_list.html', params)
        
        
def advanced_message_draft_view(request):
    
    if request.method == "GET":
        query = AdvancedMessaging.objects.filter(status="draft", created_by=request.user.kituser)
        draft_msgs_table = DraftAdvancedMessagesTable(query)
        RequestConfig(request, paginate={'per_page': 25}).configure(draft_msgs_table)
        params = {}
        params["title"] = "Draft Messages"
        params["table"] = draft_msgs_table
        params["herpath"] = (request.path.split('/'))[2]
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
    
    
    
class ReminderCreateView(PermissionRequiredMixin, CreateView):
    
    permission_required = ('messaging.add_remindermessaging','core.add_customdata')
    
    model = ReminderMessaging
    form_class = ReminderMessagingForm
    reminders_formset = ReminderFormSet
    template_name = 'messaging/reminder/new_reminder_message.html'
    
    params = {}
    
    def post(self, request, *args, **kwargs):
        
        form = self.form_class(request.POST)
        reminder_formset = ReminderFormSet(request.POST)
        
        
        if form.is_valid() and reminder_formset.is_valid():
            return self.form_valid(form, reminder_formset)
        return self.form_invalid(form, reminder_formset)
    
    
    def form_valid(self, form, formset):
        
        form.instance.created_by = self.request.user.kituser
        
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        
        return HttpResponseRedirect(reverse('messaging:reminder-message-draft', args=[self.object.pk]))
    
    
    def form_invalid(self, form, formset):
        
        return render(self.request, self.template_name, self.get_context_data())
    
    
    def get_context_data(self, **kwargs):
        context = super(ReminderCreateView, self).get_context_data(**kwargs)
        context["title"] = _("Create A Reminder Message")
        
        if self.request.POST:
            context["form"] = self.form_class(self.request.POST)
            context["reminder_formset"] = self.reminders_formset(self.request.POST)
        else:
            # it took me quite a while to realize the below was the source of my problems
            # it was overriding the form which context already had...hence I never saw all
            # the get_form queryset overrides applied.
            
            #context["form"] = self.form_class()
            context["reminder_formset"] = self.reminders_formset()
            
        return context
    
    
    ##  You could set the field here or using get_form_kwargs  as above ##
    def get_form(self, form_class=form_class):
        form = super(ReminderCreateView, self).get_form(form_class)
        form.fields["message_template"].queryset = self.request.user.kituser.get_templates().filter(active=True)
        form.fields['contact_group'].queryset = self.request.user.kituser.get_contact_groups()
        form.fields['custom_data_namespace'].queryset = self.request.user.kituser.get_custom_data()
        
        return form
    
    

class ReminderUpdateDraftView(PermissionRequiredMixin, UpdateView):
    
    permission_required = ('messaging.change_remindermessaging')
    
    model = ReminderMessaging
    form_class = ReminderMessagingForm
    template_name = 'messaging/reminder/reminder_message_draft.html'
    #reminder_formset = ReminderFormSet()
    
    params = {}
    
    def get(self, request, *args, **kwargs):
        super(ReminderUpdateDraftView, self).get(request, *args, **kwargs)
        
        choices_arr = self.object.get_custom_data_header_selected_choices()
        
        self.params["form"] = self.form_class(instance=self.object, date_column_ish=choices_arr)
        self.params["reminder_formset"] = ReminderFormSet(instance=self.object)
        
        return render(request,self.template_name, self.params)
       
    def post(self, request, *args, **kwargs):
        
        self.object = self.get_object()
        choices_arr = self.object.get_custom_data_header_selected_choices()
        form = self.form_class(request.POST or None, instance=self.object, date_column_ish=choices_arr)
        reminder_formset = ReminderFormSet(request.POST, instance=self.object)
        
        if form.is_valid() and reminder_formset.is_valid():
            return self.form_valid(form, reminder_formset)
        return self.form_invalid(form, reminder_formset)
    
    
    def form_valid(self, form, formset):
        
        self.object = form.save()
        formset.save()
        
        return HttpResponseRedirect(reverse('messaging:reminder-message-draft', args=[self.object.pk]))
    
    
    def form_invalid(self, form, reminder_formset):
        
        params = self.get_context_data()
        params["form"] = form
        params["reminder_formset"] = reminder_formset
        
        return render(self.request, self.template_name, params)
    
    
    def get_context_data(self, **kwargs):
        self.params = super(ReminderUpdateDraftView, self).get_context_data(**kwargs)
        self.params["title"] = self.object.title
        self.params["rmsgid"] = self.object.pk
        self.params["draft_time"] = self.object.last_modified
        return self.params
    
    def get_form(self, form_class=form_class):
        form = super(ReminderUpdateDraftView, self).get_form(form_class)
        form.fields["message_template"].queryset = self.request.user.kituser.get_templates().filter(active=True)
        form.fields['contact_group'].queryset = self.request.user.kituser.get_contact_groups()        
        return form
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        qs = super(ReminderUpdateDraftView, self).get_queryset(**kwargs)
        return qs.filter(created_by=self.request.user.kituser)

    
    
    
    '''
    def get_form_kwargs(self):        
        choices_arr = self.object.get_custom_data_header_selected_choices()
        kwargs = super(ReminderUpdateDraftView, self).get_form_kwargs()
        kwargs.update({'date_column_ish':choices_arr})
        return kwargs'''

def reminder_draft_view(request):
    
    if request.method == "GET":
        
        query = ReminderMessaging.objects.filter(status="draft", created_by=request.user.kituser).order_by('-last_modified')
        
        contactstable = DraftReminderMessagesTable(query)
        RequestConfig(request, paginate={'per_page': 25}).configure(contactstable)
        params = {}
        params["title"] = "Reminders"
        params["table"] = contactstable
        params["herpath"] = (request.path.split('/'))[2]
        return render(request, 'messaging/reminder/draft_reminder_messages_list.html', params)

class ReminderDeleteView(PermissionRequiredMixin, DeleteView):
    
    permission_required = ('messaging.delete_remindermessaging')
    
    model = ReminderMessaging
    #template_name = 'core/contacts/contact_confirm_delete.html' #POSTing so no need for template
    success_url = reverse_lazy('messaging:reminder-draft-messages')
    params = {}
    
    def get_context_data(self, **kwargs):
        params = super(ReminderUpdateDraftView, self).get_context_data(**kwargs)
        params["title"] = "Deleting Reminder ".format(self.object.pk)
        params["rmsgid"] = self.object.pk
        return params
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        qs = super(ReminderDeleteView, self).get_queryset(**kwargs)
        return qs.filter(created_by=self.request.user.kituser)
    
    
def message_running_status_view(request):
    
    if request.method == "GET":        
        queryset = request.user.kituser.get_running_messages()
        r_msgs_table = RunningMessagesTable(queryset)
        RequestConfig(request, paginate={'per_page': 25}).configure(r_msgs_table)
        params = {}
        
        params["title"] = "Running Messages"
        params["table"] = r_msgs_table
        return render(request, 'messaging/running_messages.html', params)
    
    
def failed_email_messages_view(request):
    
    if request.method == "GET":

        if request.user.kituser.is_admin:
            fem_table = FailedEmailMessagesTable_Admin(request.user.kituser.get_failed_email_messages())
        else:
            fem_table = FailedEmailMessagesTable(request.user.kituser.get_failed_email_messages())
        
        RequestConfig(request, paginate={'per_page': 25}).configure(fem_table)
        params = {}
        params["title"] = "Failed Email Messages"
        params["table"] = fem_table
        params["herpath"] = (request.path.split('/'))[3]

        return render(request, 'messaging/failed/email_messages_failed.html', params)
    
def failed_email_message_retry(request, pk):
    
    if request.method == "GET":
        f_email_m = FailedEmailMessage.objects.get(pk=pk, owned_by = request.user.kituser)
        f_email_m.delete()
        
        # resend the email
        _send_email(f_email_m.sms_pickled_data[0], f_email_m.sms_pickled_data[1], f_email_m.owned_by, None)
        
        return HttpResponseRedirect(reverse('messaging:email-messages-failed'))
    
def failed_kit_messages_view(request):
    
    if request.method == "GET":
        
        #qs = request.user.kituser.get_failed_email_messages()
        qs = FailedKITMessage.objects.filter(owned_by = request.user.kituser)
        fem_table = FailedKITMessagesTable(qs)
        RequestConfig(request, paginate={'per_page': 25}).configure(fem_table)
        params = {}
        params["title"] = "Failed Messages"
        params["table"] = fem_table
        params["herpath"] = (request.path.split('/'))[3]
        
        return render(request, 'messaging/failed/kit_messages_failed.html', params)
    
def failed_sms_messages_view(request):
    
    if request.method == "GET":
        
        if request.user.kituser.is_admin:
            fem_table = FailedSMSMessagesTable_Admin(request.user.kituser.get_failed_sms_messages())
        else:
            fem_table = FailedSMSMessagesTable(request.user.kituser.get_failed_sms_messages())
        
        RequestConfig(request, paginate={'per_page': 25}).configure(fem_table)
        params = {}
        params["title"] = "Failed SMS"
        params["table"] = fem_table
        params["herpath"] = (request.path.split('/'))[3]

        return render(request, 'messaging/failed/sms_messages_failed.html', params)

def failed_sms_message_retry(request, pk):
    
    if request.method == "GET":
        f_sms_m = FailedSMSMessage.objects.get(pk=pk, owned_by = request.user.kituser)
        f_sms_m.delete()
        
        # resend the sms
        _send_sms(f_sms_m.sms_pickled_data, f_sms_m.owned_by, None)
        
        return HttpResponseRedirect(reverse('messaging:sms-messages-failed'))
    
    
def failed_messaging_retry(request, pk):
    
    if request.method == "POST":
        
        if request.POST.get('message_category') == 'queued_msg':
            # run the task again...then remove from db
            qm = FailedKITMessage.objects.get(pk=pk, owned_by = request.user.kituser)
            data = qm.message_data[0]
            
            qm.delete()
            
            # Because qm is already stale, and I cannot use refresh_from_db(), since I already deleted QueuedMessage
            # I have to recreate another QueuedMessage from the previous one.            
            new_qm = QueuedMessages.objects.create(
                    message_type = getattr(data, 'message_type'),
                    message_id = getattr(data, 'message_id'),
                    message = getattr(data, 'message'),
                    delivery_time = getattr(data, 'delivery_time'),
                    recurring = getattr(data, 'recurring'),
                    created_by = getattr(data, 'created_by')
                                          )
            #process_onetime_event(queued_messages=qm.message_data)
            #process_onetime_event(list(map(lambda x : x.refresh_from_db(), qm.message_data)))
            ibd = []
            tss = ibd.append(new_qm)
            process_onetime_event(tss)
            
            
        elif request.POST.get('message_category') == 'running_msg':
            f_runng_msg = FailedKITMessage.objects.get(pk=pk, owned_by = request.user.kituser)
            
            process_reminder_event(list(map(lambda x : x.refresh_from_db(), f_runng_msg.message_data)))
        
        
        elif request.POST.get('message_category') == 'private_anniv_msg':
            f_priv_annv = FailedKITMessage.objects.get(pk=pk, owned_by = request.user.kituser)
            
            process_private_anniversary(list(map(lambda x : x.refresh_from_db(), f_priv_annv.message_data)))
            
        
        elif request.POST.get('message_category') == 'public_anniv_msg':
            f_publ_annv = FailedKITMessage.objects.get(pk=pk, owned_by = request.user.kituser)
            
            process_public_anniversary(list(map(lambda x : x.refresh_from_db(), f_publ_annv.message_data)))
        
        return HttpResponseRedirect(reverse('messaging:kit-messages-failed'))
        