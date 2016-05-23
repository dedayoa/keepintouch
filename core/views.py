from django.shortcuts import render
from django.views.generic import View
from django.http.response import HttpResponse

from django_tables2   import RequestConfig

from .models import Contact, CoGroup, CoUser
from .tables import ContactTable

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
        RequestConfig(request).configure(contactstable)
        params = {}
        params["title"] = "Contacts"
        params["table"] = contactstable
        return render(request, 'core/contacts/index.html', params)


class ContactView(View):
    
    def get(self, request, cusid):
        
        q_user = CoUser.objects.get(user=request.user)
        q_grps = q_user.group_set.all()

        contactstable = ContactTable(Contact.objects.filter(created_by_group=q_grps))
        RequestConfig(request).configure(contactstable)
        params = {}
        params["cusid"] = cusid
        params["title"] = 'Contact'
        params["table"] = contactstable
        params["grps"] = q_grps
        return render(request, 'core/contacts/index.html', params)
    
    def post(self, request):
        return HttpResponse("Hallo World")
    
class NewContactView(View):
    
    def get(self, request):
        pass
