'''
Created on Jul 28, 2016

@author: Dayo
'''

from .forms import IssueFeedbackForm


def issue_form_processor(request):
    form = IssueFeedbackForm()
    
    return {'issueform': form}