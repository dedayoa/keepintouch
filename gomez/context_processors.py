'''
Created on Jul 28, 2016

@author: Dayo
'''

from gomez.forms import IssueFeedback


def issue_form_processor(request):
    form = IssueFeedback()
    
    return {'issueform': form}