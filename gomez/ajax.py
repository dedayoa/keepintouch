'''
Created on Jul 28, 2016

@author: Dayo
'''
from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax

from .forms import IssueFeedback


@ajax
@login_required
def submit_issue_fb(request):
    
    if request.method == "POST":
        
        form = IssueFeedback(request.POST, request.FILES)
        if not form.is_valid():
            return {'errors':form.errors.as_json(escape_html=True)}
        else:
            obj = form.save(commit=False)
            obj.submitter = request.user.kituser
            obj.save()
            return {'result':'Feedback Received.<br />Thank You'}