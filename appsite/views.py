from django.shortcuts import render
from django.views.generic import View
from django.http.response import HttpResponse

# Create your views here.

class Index(View):
    
    def get(self, request):
        params = {}
        params["name"] = "Django"
        return render(request,'base.html', params)
    
    def post(self, request):
        return HttpResponse("Hallo World")

def settings(request):
    return HttpResponse("settings World")

def contacts(request):
    return HttpResponse("contact World")


class Contact(View):
    
    def get(self, request, cusid):
        params = {}
        params["cusid"] = cusid
        params["title"] = 'Contact'
        return render(request, 'contacts/index.html', params)
    
    def post(self, request):
        return HttpResponse("Hallo World")
    
class NewContact(View):
    pass
