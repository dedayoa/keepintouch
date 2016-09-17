import sys
import datetime


from django import forms
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.views.generic import View, TemplateView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib import messages as flash_messages
from django.utils import timezone

from django_tables2 import RequestConfig

from .models import Contact, CoUserGroup, KITUser, Event, PublicEvent, MessageTemplate,\
                    SMTPSetting, ContactGroup, SMSTransfer, UploadedContact, CustomData, OrganizationContact
from .forms import ContactForm, NewContactForm, EventFormSet, KITUserForm, ExistingUserForm,\
                    EventFormSetHelper, PublicEventForm, MessageTemplateForm, SMTPSettingForm, \
                    UserGroupSettingForm, NewUserForm, ContactGroupForm, SMSTransferForm,\
                    ContactImportForm, PersonalProfileForm, CustomDataIngestForm, KITUBalanceForm,\
                    VerifyAccountForm, OrganizationContactForm, ContactSearchForm
from .tables import ContactTable, PrivateEventTable, PublicEventTable, TemplateTable,\
                    KITUsersTable, SMTPSettingsTable, UserGroupsSettingsTable, ContactGroupsSettingsTable,\
                    SMSTransferHistoryTable, UploadedContactFileHistoryTable, CustomDataStoreTable
                    
from .tables import ContactTable_Admin
from django.views.generic.edit import UpdateView, DeleteView, CreateView,\
    FormMixin
    

from django_select2.views import AutoResponseView

from django.core import mail
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend
from django.contrib.messages.api import get_messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import logout, get_user_model

from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import user_passes_test

from messaging.helper import SMTPHelper

from sitegate.decorators import signin_view, redirect_signedin, signup_view
from sitegate.signup_flows.classic import ClassicSignup
from sitegate.signup_flows.modern import ModernSignup

from django.conf import settings
import mimetypes
from gomez.models import KITBilling

from stronghold.decorators import public
from django.views.decorators.csrf import csrf_exempt
from core.models import KITUBalance
from django.db.utils import IntegrityError


from watson import search as watson
from django.utils.safestring import mark_safe


# Create your views here.
@signin_view(template='core/sitegate/sitegate-myfoundation.html', redirect_to='core:dashboard-view')
@redirect_signedin('core:dashboard-view')
def entrance(request):
    
    @csrf_exempt
    def nocsrf_path(request):
        return render(request, 'core/crawler_access.html', {'title': 'Welcome'})
    
    if request.GET.get('next') == '/gcrawler/': #i came here from gcrawler
        return nocsrf_path(request)
    else:
        return render(request, 'core/access.html', {'title': 'Welcome'})


@signup_view(template='core/sitegate/sitegate-signup-foundation.html', flow=ModernSignup)
def register_free_trial(request):
    return render(request, 'core/free_trial_register.html',{'title':'Register for a Free Trial'})


def validate_user_details(request):
    form = VerifyAccountForm(user=request.user)
    try:
        form_2 = OrganizationContactForm(instance=request.user.kituser.address or request.user.kituser.parent.address)
    except AttributeError:
        form_2 = OrganizationContactForm()
    
    params = {}
    params['title'] = 'Validate User Details'
    params['form'] = form
    params['form_2'] = form_2
    params['body_class'] = 'verify-account-gate'
    return render(request, 'core/validate_email_phone.html', params)

def crawler_entrance(request):
    pass


def exitdoor(request):
    logout(request)
    return HttpResponseRedirect('/')


class Index(View):
    
    def get(self, request):
        

        params = {}
        params["name"] = "Django"
        return render(request,'core/base.html', params)
    
    def post(self, request):
        return HttpResponse("Hallo World")


class DashboardView(TemplateView):
    
    template_name = 'core/dashboard.html'
    params = {}
    
    
    def get(self,request):
        
        if request.user.kituser.is_admin:
        
            now = timezone.now()
            svn_days_to_come = now + datetime.timedelta(days=7)
            tty_days_to_come = now + datetime.timedelta(days=30)
            
            private_events = request.user.kituser.get_private_events().filter(date__range = (now, svn_days_to_come))[:10]
            public_events = request.user.kituser.get_public_events().filter(date__range = (now, tty_days_to_come))[:10]
            #
            #
            self.params["title"] = "Dashboard"
            self.params["body_class"] = "dashboard"
            self.params["priv_annv"] = private_events
            self.params["publ_annv"] = public_events
            self.params["is_saas"] = settings.KIT_IS_SAAS
            return render(request,self.template_name, self.params)
        
        else:
            return HttpResponseRedirect(reverse('messaging:new-standard-message'))

def contacts(request):
    
    if request.method == "GET":
        if not request.GET.get('search_query',''):
            #q_grps = user_q.group.all() #groups the user belongs to
            #user_s_group = CoUserGroup.objects.filter()
            #Contact.objects.filter()
            if request.user.kituser.is_admin:
                contactstable = ContactTable_Admin(request.user.kituser.get_contacts())
            else:
                contactstable = ContactTable(request.user.kituser.get_contacts())
            RequestConfig(request, paginate={'per_page': 25}).configure(contactstable)
            params = {}
            params["title"] = "Contacts"
            params["page_title"] = "Contacts"
            params["table"] = contactstable
            params["contacts_search_form"] = ContactSearchForm
            return render(request, 'core/contacts/index.html', params)
        else:
            queryp = request.GET.get('search_query')
            form = ContactSearchForm(request.GET)
            if form.is_valid():
                print(queryp)
                
                params = {}
                params["title"] = "Search Result"
                params["page_title"] = mark_safe("Search Result <small>{}</small>".format(queryp))
                
                #search_results = watson.filter(Contact, queryp)
                #watson.search(queryp, models=(Contact.objects.filter(title="foo"),))
                
                if request.user.kituser.is_admin:
                    search_results = watson.filter(request.user.kituser.get_contacts(), queryp)
                    contactstable = ContactTable_Admin(search_results)
                else:
                    search_results = watson.filter(request.user.kituser.get_contacts(), queryp)
                    contactstable = ContactTable(search_results)
                RequestConfig(request, paginate={'per_page': 25}).configure(contactstable)
                params["table"] = contactstable
                params["contacts_search_form"] = ContactSearchForm(initial={'search_query': queryp})
                return render(request, 'core/contacts/index.html', params)
            
            return render(request, 'core/contacts/index.html', params)
        


class ContactView(View):
    
    form_class = ContactForm
    event_formset = EventFormSet()
    template_name = 'core/contacts/contact_detail.html'
    params = {}
    
    def get(self, request, contactid):
        q_user = get_object_or_404(Contact, pk=contactid)
        self.params["form"] = self.form_class(instance=q_user)
        self.params["title"] = "Contact {}".format(contactid)
        self.params["contactid"] = contactid
        
        self.params["event_formset"] = EventFormSet(instance=q_user)
        
        return render(request,self.template_name, self.params)
    
    def post(self, request, contactid):
        
        q_user = get_object_or_404(Contact, pk=contactid)
        form = self.form_class(request.POST or None, instance=q_user)
        self.params["title"] = "Contact {}".format(contactid)
        if form.is_valid():
            #self.params["data"] = request.POST.get()
            form.save()
            #group = CoGroup.objects.get(pk=request.POST.get('created_by_group'))
            #a = Contact(request.POST)
            '''data = {
                    #'slug' : contactid,
                    'salutation':request.POST.get('salutation',''),
                    'first_name':request.POST.get('first_name',''),
                    'last_name':request.POST.get('last_name',''),
                    'email':request.POST.get('email',''),
                    'phone':request.POST.get('phone',''),
                    'active':request.POST.get('active',''),
                    'created_by_group': request.POST.get('created_by_group')
                    }
            c = Contact(data)
            c.save()'''
            #a.save()
            return HttpResponseRedirect(reverse('core:contact-detail', args=[contactid]))
        
        return render(request, self.template_name, self.params)

#The regular class based view is above.
class ContactViewView(UpdateView):

    model = Contact
    form_class = ContactForm
    template_name = 'core/contacts/contact_detail.html'
    event_formset = EventFormSet()
    params = {}
    #event_formset_helper = EventFormSetHelper()
    
    def get(self, request, *args, **kwargs):
        super(ContactViewView, self).get(request, *args, **kwargs)
        #q1 = Contact.objects.filter(pk=self.object.pk)
        
        #q1 = get_object_or_404(Contact, pk=self.object.pk)
        #queryset = Event.objects.filter(contact=q1)
        #q2 = q1.event_set.all()
        #self.object = self.get_object() #can pass queryset
        #form_class = self.get_form_class()
        #form = self.get_form(form_class)
        event_line_item_form = EventFormSet(instance=self.object)
        
        
        self.params["form"] = self.form_class(instance=self.object)
        
        self.params["event_formset"] = event_line_item_form
        
        return render(request,self.template_name, self.params)
        '''
        return self.render_to_response(self.get_context_data(
                form = form,
                event_line_item_form = event_line_item_form
                )
            )
        '''
        
        
    def post(self, request, *args, **kwargs):
        #super(ContactViewView, self).post(request, *args, **kwargs)
        self.object = self.get_object()
        #form_class = self.get_form_class()
        form = self.get_form(self.form_class)
        
        #form = self.form_class(instance=self.object)
        event_formset = EventFormSet(request.POST, instance=self.object)
        
        
        if form.is_valid() and event_formset.is_valid():
            return self.form_valid(form, event_formset)
        return self.form_invalid(form, event_formset)
        
        #return render(request,self.template_name, self.params)
    
    def form_valid(self, form, event_line_item_form):
        
        self.object = form.save()
        #event_line_item_form.instance = self.object
        event_line_item_form.save()
        return HttpResponseRedirect(reverse('core:contact-detail', args=[self.object.pk]))
        #return HttpResponseRedirect(self.object.get_absolute_url())
    
    def form_invalid(self, form, event_line_item_form):
        
        flash_messages.add_message(self.request, flash_messages.INFO, 'The last action failed due to error in submission.')
        return HttpResponseRedirect(reverse('core:contact-detail', args=[self.object.pk]))
        '''
        return self.render_to_response(
            self.get_context_data(
                form = form,
                event_line_item_form = event_line_item_form
            )
        )'''
    
    def get_context_data(self, **kwargs):
        self.params = super(ContactViewView, self).get_context_data(**kwargs)
        self.params["title"] = "Contact {}".format(self.object.pk)
        self.params["contactid"] = self.object.pk
        return self.params
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        return self.request.user.kituser.get_contacts()

class ContactDeleteView(DeleteView):
    
    model = Contact
    #template_name = 'core/contacts/contact_confirm_delete.html' #POSTing so no need for template
    success_url = reverse_lazy('core:contacts-list')
    params = {}
    
    def get_context_data(self, **kwargs):
        params = super(ContactViewView, self).get_context_data(**kwargs)
        params["title"] = "Deleting Contact ".format(self.object.pk)
        params["contactid"] = self.object.pk
        return params
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        return self.request.user.kituser.get_contacts()

    
class ContactCreateView(CreateView):
    
    model = Contact
    form_class = NewContactForm
    template_name = 'core/contacts/new_contact.html'
    #success_url = reverse_lazy('core:contacts-list')
    
    def form_valid(self, form):
        form.instance.kit_user = self.request.user.kituser

        return super(ContactCreateView, self).form_valid(form)
        #return HttpResponseRedirect(reverse('core:contact-detail', args=[self.object.pk])) 
    
    def get_context_data(self, **kwargs):
        self.params = super(ContactCreateView, self).get_context_data(**kwargs)
        self.params["title"] = "New"
        return self.params
    
    def get_success_url(self):
        return reverse('core:contact-detail', kwargs={'pk': self.object.pk}) #http://stackoverflow.com/questions/11027996/success-url-in-updateview-based-on-passed-value
    
    #fields = ['salutation','first_name','last_name','email','phone','active','created_by_group']


def privateevents(request):
    
    if request.method == "GET":
        q_user = KITUser.objects.get(user=request.user)
        #q_grps = q_user.group.all() #groups the user belongs to
        #q_contacts = Contact.objects.filter(created_by_group__in=q_grps)

        eventstable = PrivateEventTable(q_user.get_private_events())
        RequestConfig(request, paginate={'per_page': 25}).configure(eventstable)
        params = {}
        params["title"] = "Events"
        params["table"] = eventstable
        return render(request, 'core/events/index.html', params)
    
def publicevents(request):
    
    if request.method == "GET":
        q_user = KITUser.objects.get(user=request.user)
        #q_grps = q_user.group.all() #groups the user belongs to
        #q_publ_ev = PublicEvent.objects.filter(event_group__in=q_grps)

        eventstable = PublicEventTable(q_user.get_public_events())
        RequestConfig(request, paginate={'per_page': 25}).configure(eventstable)
        params = {}
        params["title"] = "Public Events"
        params["table"] = eventstable
        return render(request, 'core/events/public_events_index.html', params)
    
class PublicEventCreateView(CreateView):
    
    model = PublicEvent
    form_class = PublicEventForm
    template_name = 'core/events/new_public_event.html'
    
    def form_valid(self, form):
        form.instance.kit_user = self.request.user.kituser

        return super(PublicEventCreateView, self).form_valid(form)
    
    def get_form(self, form_class=form_class):
        form = super(PublicEventCreateView, self).get_form(form_class)
        form.fields["recipients"].queryset = self.request.user.kituser.get_contacts()       
        return form

   
class PublicEventUpdateView(UpdateView):
    
    model = PublicEvent
    form_class = PublicEventForm
    template_name = 'core/events/public_event_detail.html'
    params = {}
    '''
    def get(self, request, *args, **kwargs):
        super(PublicEventUpdateView, self).get(request, *args, **kwargs)
        self.params["form"] = self.form_class(instance=self.object)
        self.params["publiceventid"] = self.object.pk       
        return render(request,self.template_name, self.params)'''
    
    def get_context_data(self, **kwargs):
        params = super(PublicEventUpdateView, self).get_context_data(**kwargs)
        params["publiceventid"] = self.object.pk
        return params
    
    
    def get_form(self, form_class=form_class):
        form = super(PublicEventUpdateView, self).get_form(form_class)
        form.fields["recipients"].queryset = self.request.user.kituser.get_contacts()       
        return form
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        return self.request.user.kituser.get_public_events()
    
    
    
class PublicEventDeleteView(DeleteView):
    
    model = PublicEvent
    #template_name = 'core/contacts/contact_confirm_delete.html' #POSTing so no need for template
    success_url = reverse_lazy('core:public-events-list')
    #params = {}
    
    def get_context_data(self, **kwargs):
        params = super(PublicEventDeleteView, self).get_context_data(**kwargs)
        params["title"] = "Deleting Public Event {} ".format(self.object.title)
        params["publiceventid"] = self.object.pk
        return params
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        return self.request.user.kituser.get_public_events()
    
    
def templates(request):
    
    if request.method == "GET":
        q_user = KITUser.objects.get(user=request.user)
        #q_grps = q_user.group.all() #groups the user belongs to
        #q_contacts = Contact.objects.filter(created_by_group__in=q_grps)

        templatestable = TemplateTable(q_user.get_templates())
        RequestConfig(request, paginate={'per_page': 25}).configure(templatestable)
        params = {}
        params["title"] = "Templates"
        params["table"] = templatestable
        return render(request, 'core/templates/index.html', params)
    
class MessageTemplateUpdateView(PermissionRequiredMixin, UpdateView):
    
    permission_required = 'core.change_messagetemplate'
    
    model = MessageTemplate
    form_class = MessageTemplateForm
    template_name = 'core/templates/template_detail.html'
    
    def get_context_data(self, **kwargs):
        params = super(MessageTemplateUpdateView, self).get_context_data(**kwargs)
        params["msgtemplateid"] = self.object.pk
        return params
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        return self.request.user.kituser.get_templates()
    
    def get_form(self, form_class=form_class):
        form = super(MessageTemplateUpdateView, self).get_form(form_class)
        form.fields["cou_group"].queryset = self.request.user.kituser.get_user_groups()
        form.fields["smtp_setting"].queryset = self.request.user.kituser.get_smtp_items()    
        return form
    
    
class MessageTemplateCreateView(PermissionRequiredMixin, CreateView):
    
    permission_required = 'core.add_messagetemplate'
    
    model = MessageTemplate
    form_class = MessageTemplateForm
    template_name = 'core/templates/new_template.html'
    
    def form_valid(self, form):
        form.instance.kit_admin = self.request.user.kituser

        return super(MessageTemplateCreateView, self).form_valid(form)

    def get_form(self, form_class=form_class):
        form = super(MessageTemplateCreateView, self).get_form(form_class)
        form.fields["cou_group"].queryset = self.request.user.kituser.get_user_groups()
        form.fields["smtp_setting"].queryset = self.request.user.kituser.get_smtp_items()    
        return form
    
class MessageTemplateDeleteView(PermissionRequiredMixin, DeleteView):
    
    permission_required = 'core.delete_messagetemplate'
    
    model = MessageTemplate
    success_url = reverse_lazy('core:templates-list')
    
    def get_context_data(self, **kwargs):
        params = super(MessageTemplateDeleteView, self).get_context_data(**kwargs)
        params["title"] = "Deleting Template {} ".format(self.object.title)
        return params
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        return self.request.user.kituser.get_templates()
    

def kituser_settings(request):
    
    if request.method == "GET":
        q_admin = KITUser.objects.get(user=request.user)
        #q_admin = User.objects.get(username = request.user)

        kituserstable = KITUsersTable(q_admin.get_kitusers())
        RequestConfig(request, paginate={'per_page': 10}).configure(kituserstable)
        params = {}
        params["title"] = "User Settings"
        params["table"] = kituserstable
        return render(request, 'core/settings/users/index.html', params)
    
class UserCreateView(PermissionRequiredMixin, View):
    
    permission_required = 'core.add_kituser'
    
    model_1 = User
    model_2 = KITUser
    template_name = 'core/settings/users/new_user.html'
    params = {}
    
    form_1 = NewUserForm
    form_2 = KITUserForm
        
    def get(self, request):
        
        q_admin = KITUser.objects.get(user=request.user)
        
        nuform = NewUserForm(instance=None, prefix="userform", kituser=self.request.user.kituser)
        
        self.params["title"] = "New User"
        self.params["form_1"] = nuform
        self.params["form_2"] = self.form_2(instance=None, prefix="kituform")
        
        return render(request, self.template_name, self.params)
    
    
    def post(self, request):

        #k_user = get_object_or_404(KITUser, pk=pk,parent=request.user.kituser)
        #uzr = k_user.user
        
        nuform = NewUserForm(request.POST or None, prefix="userform", instance=None, kituser=self.request.user.kituser)
        self.params["form_1"] = userform = nuform
        self.params["form_2"] = kituform = self.form_2(request.POST or None, prefix="kituform", instance=None)
        
        if userform.is_valid() and kituform.is_valid():
            try:
                with transaction.atomic():
                    f1 = userform.save()
                    
                    # Assign this user to the standard kituser group
                    group = Group.objects.get(id=settings.STANDARD_KITUSER_GROUP_PERMS_ID)
                    f1.groups.add(group)
                    
                    f2 = kituform.save(commit=False)
                    f2.user = f1
                    f2.parent= request.user.kituser
                    f2.save()
            
            
                
                    
                return HttpResponseRedirect(reverse('core:kituser-detail', args=[f2.pk]))
            except IntegrityError:
                flash_messages.add_message(request, flash_messages.INFO, "Username already exists" )
                return render(request, self.template_name, self.params)
        
        return render(request, self.template_name, self.params)       
        #transaction.on_commit(
        #    lambda :HttpResponseRedirect(reverse('core:kituser-detail', args=[f2.pk]))
        #)      

    
    def get_success_url(self):
        return reverse('core:kituser-detail', kwargs={'pk': self.object.pk})
    

class KITUserUpdateView(PermissionRequiredMixin, View):
    
    permission_required = 'core.change_kituser'
    
    model_1 = User
    model_2 = KITUser
    model_3 = KITUBalance
    template_name = 'core/settings/users/kituser_detail.html'
    params = {}
    
    form_1 = ExistingUserForm
    form_2 = KITUserForm
    form_3 = KITUBalanceForm
    
    
    def get(self, request, pk):
        
        q_admin = KITUser.objects.get(user=request.user)
        
        if q_admin:
            k_user = get_object_or_404(KITUser, pk=pk,parent=q_admin)
            uzr = k_user.user
            k_user_balance = request.user.kituser.kitubalance 
        
        self.params["title"] = "Edit User"
        self.params["uzrname"] = uzr.username
        self.params["last_login"] = uzr.last_login
        self.params["date_joined"] = uzr.date_joined
        self.params["form_1"] = self.form_1(instance=uzr, prefix="userform")
        self.params["form_2"] = self.form_2(instance=k_user, prefix="kituform")        
        self.params["form_3"] = self.form_3(instance=k_user_balance, prefix="kitubalanceform")
        
        return render(request, self.template_name, self.params)
    
    
    def post(self, request, pk):

        k_user = get_object_or_404(KITUser, pk=pk,parent=request.user.kituser)
        uzr = k_user.user
        
        userform = self.form_1(request.POST, prefix="userform", instance=uzr)
        kituform = self.form_2(request.POST, prefix="kituform", instance=k_user)
        
        if userform.is_valid() and kituform.is_valid():
            
            f1 = userform.save()
            f2 = kituform.save(commit=False)
            f2.user = f1
            f2.save()
                
            
        return HttpResponseRedirect(reverse('core:kituser-detail', args=[pk]))   

class KITUserPersonalProfileView(View):
    
    model_1 = User
    model_2 = KITUser
    model_3 = KITUBalance
    template_name = 'core/settings/users/kituser_detail.html'
    params = {}
    
    form_1 = PersonalProfileForm
    form_2 = KITUserForm
    form_3 = KITUBalanceForm

    
    def get(self, request):
        
        
        k_user = request.user.kituser
        uzr = request.user
        k_user_balance = request.user.kituser.kitubalance 
        
        self.params["title"] = "Edit User"
        self.params["uzrname"] = uzr.username
        self.params["last_login"] = uzr.last_login
        self.params["date_joined"] = uzr.date_joined
        self.params["form_1"] = self.form_1(instance=uzr, prefix="userform")
        self.params["form_2"] = self.form_2(instance=k_user, prefix="kituform")
        self.params["form_3"] = self.form_3(instance=k_user_balance, prefix="kitubalanceform")
        
        return render(request, self.template_name, self.params)
    
    
    def post(self, request):

        k_user = request.user.kituser
        uzr = k_user.user
        
        userform = self.form_1(request.POST, prefix="userform", instance=uzr)
        kituform = self.form_2(request.POST, prefix="kituform", instance=k_user)
        
        if userform.is_valid() and kituform.is_valid():
            
            f1 = userform.save()
            f2 = kituform.save(commit=False)
            f2.user = f1
            f2.save()
                
            
        return HttpResponseRedirect(reverse('core:kituser-personal-profile'))    


   
def smtp_settings(request):
    
    if request.method == "GET":
        q_admin = KITUser.objects.get(user=request.user)

        smtpsetstable = SMTPSettingsTable(q_admin.get_smtp_items())
        RequestConfig(request, paginate={'per_page': 25}).configure(smtpsetstable)
        params = {}
        params["title"] = "SMTP Settings"
        params["table"] = smtpsetstable
        return render(request, 'core/settings/smtp/index.html', params)
    
class SMTPUpdateView(UpdateView):
    
    model = SMTPSetting
    form_class = SMTPSettingForm
    template_name = 'core/settings/smtp/smtp_setting_detail.html'
    
    def get_context_data(self, **kwargs):
        params = super(SMTPUpdateView, self).get_context_data(**kwargs)
        params["smtpsettingid"] = self.object.pk
        params["messages"] = get_messages(self.request)
        return params
    
    def get_form(self, form_class=form_class):
        form = super(SMTPUpdateView, self).get_form(form_class)
        form.fields["cou_group"].queryset = self.request.user.kituser.get_user_groups() 
        return form
       
    
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        return self.request.user.kituser.get_smtp_items()
    
class SMTPCreateView(CreateView):
    
    model = SMTPSetting
    form_class = SMTPSettingForm
    template_name = 'core/settings/smtp/new_smtp_setting.html'
    
    def form_valid(self, form):
        form.instance.kit_admin = self.request.user.kituser

        return super(SMTPCreateView, self).form_valid(form)
    
    def get_form(self, form_class=form_class):
        form = super(SMTPCreateView, self).get_form(form_class)
        form.fields['cou_group'].queryset = self.request.user.kituser.get_user_groups()
        
        return form
        
    
class SMTPDeleteView(DeleteView):
    
    model = SMTPSetting
    success_url = reverse_lazy('core:smtp-settings-list')
    
    def get_context_data(self, **kwargs):
        params = super(SMTPDeleteView, self).get_context_data(**kwargs)
        params["title"] = "Deleting SMTP Setting {} ".format(self.object.title)
        return params
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        return self.request.user.kituser.get_smtp_items()
    
class CheckSMTPServerView(View):
    
    params = {}
    
    def post(self, request, pk):
        
        if request.user.kituser.is_admin:
            #pulling from DB, not Form
            smtp_profile = get_object_or_404(SMTPSetting, pk=pk, kit_admin=request.user.kituser)
            
            eh = SMTPHelper(smtp_profile)
            er = eh.test_smtp_server()
            
            if er == True:
                flash_messages.add_message(request, flash_messages.INFO, "Email SMTP - Test OK" )
            else:
                flash_messages.add_message(request, flash_messages.INFO,'Email SMTP - Test Failed')
                flash_messages.add_message(request, flash_messages.INFO, er[1])
                
            
            return HttpResponseRedirect(reverse('core:smtp-detail', args=[pk]))
        

       
def usergroup_settings(request):
    
    if request.method == "GET":
        q_admin = KITUser.objects.get(user=request.user)
    
        ugroupsstable = UserGroupsSettingsTable(q_admin.get_user_groups())
        RequestConfig(request, paginate={'per_page': 25}).configure(ugroupsstable)
        params = {}
        params["title"] = "User Groups"
        params["table"] = ugroupsstable
        return render(request, 'core/settings/user_groups/index.html', params)
    
class UserGroupUpdateView(PermissionRequiredMixin, UpdateView):
    
    permission_required = 'core.change_cousergroup'
    
    model = CoUserGroup
    form_class = UserGroupSettingForm
    template_name = 'core/settings/user_groups/user_group_detail.html'
    
    def get_context_data(self, **kwargs):
        params = super(UserGroupUpdateView, self).get_context_data(**kwargs)
        params["usergroupid"] = self.object.pk
        params["gptitle"] = self.object.title
        return params
    
    def get_form_kwargs(self):
        kwargs = super(UserGroupUpdateView, self).get_form_kwargs()
        kwargs.update({'kituser': self.request.user.kituser})
        return kwargs
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        return self.request.user.kituser.get_user_groups()    
    
class UserGroupCreateView(PermissionRequiredMixin, CreateView):
    
    permission_required = 'core.add_cousergroup'
    
    model = CoUserGroup
    form_class = UserGroupSettingForm
    template_name = 'core/settings/user_groups/new_user_group.html'
    
    
    def form_valid(self, form):
        form.instance.kit_admin = self.request.user.kituser

        return super(UserGroupCreateView, self).form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super(UserGroupCreateView, self).get_form_kwargs()
        kwargs.update({'kituser': self.request.user.kituser})
        return kwargs
    
class UserGroupDeleteView(DeleteView):
    
    model = CoUserGroup
    success_url = reverse_lazy('core:usergroup-list')
    
    def get_context_data(self, **kwargs):
        params = super(UserGroupDeleteView, self).get_context_data(**kwargs)
        params["title"] = "Deleting User Group {} ".format(self.object.title)
        params["usergroupid"] = self.object.pk
        return params
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        return self.request.user.kituser.get_user_groups()
    
def contactgroups(request):
    
    if request.method == "GET":
    
        congrpstable = ContactGroupsSettingsTable(request.user.kituser.get_contact_groups())
        RequestConfig(request, paginate={'per_page': 25}).configure(congrpstable)
        params = {}
        params["title"] = "Contact Groups"
        params["table"] = congrpstable
        return render(request, 'core/contacts/groups/index.html', params)
    
class ContactGroupUpdateView(UpdateView):
    
    model = ContactGroup
    template_name = 'core/contacts/groups/contactgroup_detail.html'
    form_class = ContactGroupForm
    
    def get_context_data(self, **kwargs):
        params = super(ContactGroupUpdateView, self).get_context_data(**kwargs)
        params["contactgroupid"] = self.object.pk
        return params
    
    
    def get_form_kwargs(self):
        kwargs = super(ContactGroupUpdateView, self).get_form_kwargs()
        kwargs.update({'kituser': self.request.user.kituser})
        return kwargs
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        qs = super(ContactGroupUpdateView, self).get_queryset(**kwargs)
        return qs.filter(kit_user=self.request.user.kituser)


class ContactGroupDeleteView(DeleteView):
    
    model = ContactGroup
    success_url = reverse_lazy('core:contactgroup-detail')
    
    def get_context_data(self, **kwargs):
        params = super(ContactGroupDeleteView, self).get_context_data(**kwargs)
        params["title"] = "Deleting Contact Group"
        return params
    
    def get_queryset(self, **kwargs):
        # user should not be able to view/edit only settings of her group/company
        qs = super(ContactGroupDeleteView, self).get_queryset(**kwargs)
        return qs.filter(kit_user=self.request.user.kituser)
    
class ContactGroupCreateView(CreateView):
    
    model = ContactGroup
    form_class = ContactGroupForm
    template_name = 'core/contacts/groups/new_contactgroup.html'
    
    
    def form_valid(self, form):
        form.instance.kit_user = self.request.user.kituser
        return super(ContactGroupCreateView, self).form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super(ContactGroupCreateView, self).get_form_kwargs()
        kwargs.update({'kituser': self.request.user.kituser})
        return kwargs
    
    def get_context_data(self, **kwargs):
        params = super(ContactGroupCreateView, self).get_context_data(**kwargs)
        params["title"] = "New Contact List"
        return params
    
    
class SMSBalanceTransferView(PermissionRequiredMixin, TemplateView):
    
    permission_required = 'core.add_smstransfer'
    
    template_name = "core/settings/accounts/sms_transfer_and_log.html"
    params = {}

    
    def get(self, request):
        self.params['total_balance'] = request.user.kituser.kitubalance.sms_balance
        
        smshtable = SMSTransferHistoryTable(SMSTransfer.objects.filter(created_by = request.user.kituser).order_by('-transaction_date'))
        RequestConfig(request, paginate={'per_page': 50}).configure(smshtable)
        
        self.params['users'] = request.user.kituser.get_kitusers()
        transfer_form = SMSTransferForm(crequest=request)
        
        self.params['transfer_form'] = transfer_form
        self.params['table'] = smshtable
        self.params["title"] = "SMS Transfer & History"
        
        return render(request, self.template_name, self.params)
    
    
class AccountManagementView(TemplateView):
    
    template_name = 'core/settings/accounts/accounts_landing.html'
    params = {}
    
    def get(self, request):
        
        self.params["sms_balance"] = request.user.kituser.kitubalance.sms_balance
        self.params["billing_info"] = request.user.kituser.kitbilling
        self.params["syssetid"] = request.user.kituser.kitsystem.id
        self.params["title"] = "Manage Account"
        return render(request, self.template_name, self.params)
    
    
class ContactImportView(TemplateView):
    
    template_name = 'core/data_mgmt/import_contact.html'
    params = {}
    
    def get(self, request):
        import_form = ContactImportForm()
        self.params["title"] = "Import Contacts"
        self.params['import_form'] = import_form
        self.params['file_max_size'] = settings.MAX_UPLOAD_FILE_SIZE
        self.params['allowed_extensions'] = (mimetypes.guess_extension(alwdt) for alwdt in settings.ALLOWED_CONTENT_TYPES)
        
                
        uphistable = UploadedContactFileHistoryTable(UploadedContact.objects.filter(uploaded_by = request.user.kituser).order_by('-upload_date'))
        RequestConfig(request, paginate={'per_page': 30}).configure(uphistable)
        self.params["table"] = uphistable
        
        return render(request, self.template_name, self.params)




class CustomDataView(PermissionRequiredMixin, TemplateView):
    
    permission_required = 'core.add_customdata'
    
    template_name = 'core/data_mgmt/custom_data.html'
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
    
    def get_queryset(self, **kwargs):
        qs = super(CustomDataView, self).get_queryset(**kwargs)
        return qs.filter(kit_user=self.request.user.kituser)