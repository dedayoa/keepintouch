from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, reverse

from django_tables2   import RequestConfig

from .models import Contact, CoGroup, CoUser, Event
from .forms import ContactForm, NewContactForm, EventFormSet, EventFormSetHelper
from .tables import ContactTable
from django.views.generic.edit import UpdateView, DeleteView, CreateView

# Create your views here.

class Index(View):
    
    def get(self, request):
        

        params = {}
        params["name"] = "Django"
        return render(request,'core/base.html', params)
    
    def post(self, request):
        return HttpResponse("Hallo World")

def settings(request):
    return HttpResponse("settings World")

def contacts(request):
    
    if request.method == "GET":
        q_user = CoUser.objects.get(user=request.user)
        q_grps = q_user.group.all() #groups the user belongs to
        contactstable = ContactTable(Contact.objects.filter(created_by_group__in=q_grps))
        RequestConfig(request, paginate={'per_page': 25}).configure(contactstable)
        params = {}
        params["title"] = "Contacts"
        params["table"] = contactstable
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

class ContactDeleteView(DeleteView):
    
    model = Contact
    #template_name = 'core/contacts/contact_confirm_delete.html' #POSTing so no need for template
    success_url = reverse_lazy('core:contacts-list')
    
    def get_context_data(self, **kwargs):
        params = super(ContactViewView, self).get_context_data(**kwargs)
        params["title"] = "Deleting Contact ".format(self.object.pk)
        params["contactid"] = self.object.pk
        return params

    
class ContactCreateView(CreateView):
    
    model = Contact
    form_class = NewContactForm
    template_name = 'core/contacts/new_contact.html'
    success_url = reverse_lazy('core:contacts-list')
    
    def get_context_data(self, **kwargs):
        params = super(ContactCreateView, self).get_context_data(**kwargs)
        params["title"] = "New"
        return params
    
    #fields = ['salutation','first_name','last_name','email','phone','active','created_by_group']

class EventCreateView(CreateView):
    
    model = Event