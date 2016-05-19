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

def contact(request):
    return HttpResponse("contact World")
