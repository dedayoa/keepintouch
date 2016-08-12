'''
Created on Jul 28, 2016

@author: Dayo
'''

import tablib
import uuid
import os
import base64
from cryptography.fernet import Fernet

from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile, File
from django.utils.text import slugify

from .forms import IssueFeedbackForm
#from munch import munchify



@ajax
@login_required
def submit_issue_fb(request):
    
    if request.method == "POST":
        
        form = IssueFeedbackForm(request.POST, request.FILES)
        if not form.is_valid():
            return {'errors':form.errors.as_json(escape_html=True)}
        else:
            obj = form.save(commit=False)
            obj.submitter = request.user.kituser
            obj.save()
            return {'result':'Feedback Received.<br />Thank You'}
        
        
