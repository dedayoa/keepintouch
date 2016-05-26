from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, reverse

from django_tables2   import RequestConfig

from .models import Contact, CoGroup, CoUser
from .forms import ContactForm, NewContactForm
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
    template_name = 'core/contacts/contact_detail.html'
    params = {}
    
    def get(self, request, contactid):
        q_user = get_object_or_404(Contact, pk=contactid)
        self.params["form"] = self.form_class(instance=q_user)
        self.params["title"] = "Contact {}".format(contactid)
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

class ContactViewView(UpdateView):
    
    model = Contact
    form_class = ContactForm
    template_name = 'core/contacts/contact_detail.html'
    
    def get_context_data(self, **kwargs):
        params = super(ContactViewView, self).get_context_data(**kwargs)
        params["title"] = "Contact {}".format(self.object.pk)
        return params

class ContactDeleteView(DeleteView):
    
    model = Contact
    
    template_name = 'core/contacts/contact_detail.html'
    success_url = reverse_lazy('core:contacts-list')
    
class ContactCreateView(CreateView):
    
    model = Contact
    form_class = NewContactForm
    template_name = 'core/contacts/contact_detail.html'
    success_url = "/"
    
    def get_context_data(self, **kwargs):
        params = super(ContactCreateView, self).get_context_data(**kwargs)
        params["title"] = "New"
        return params
    
    #fields = ['salutation','first_name','last_name','email','phone','active','created_by_group']

