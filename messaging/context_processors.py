'''
Created on Jul 28, 2016

@author: Dayo
'''

from .forms import IssueFeedbackForm
from cacheops import cached_as
from .models import FailedEmailMessage, FailedKITMessage, FailedSMSMessage


def issue_form_processor(request):
    form = IssueFeedbackForm()
    
    return {'issueform': form}



def total_failed_messages_count(request):
    
    if hasattr(request.user, 'kituser'):
    
        @cached_as(FailedEmailMessage.objects.filter(owned_by = request.user.kituser), 
                   FailedSMSMessage.objects.filter(owned_by = request.user.kituser), 
                   FailedKITMessage.objects.filter(owned_by = request.user.kituser),
                   timeout=120) 
        def _total_failed_msgs():
        
            if request.user.kituser.is_admin:
                t_email = FailedEmailMessage.objects.filter(owned_by__parent = request.user.kituser).count()
                t_sms = FailedSMSMessage.objects.filter(owned_by__parent = request.user.kituser).count()
                t_kitm = FailedKITMessage.objects.filter(owned_by__parent = request.user.kituser).count()
            else:
                t_email = FailedEmailMessage.objects.filter(owned_by = request.user.kituser).count()
                t_sms = FailedSMSMessage.objects.filter(owned_by = request.user.kituser).count()
                t_kitm = FailedKITMessage.objects.filter(owned_by = request.user.kituser).count()
            
            return {'total_failed_msg_count' : t_email+t_kitm+t_sms}
        
        return _total_failed_msgs()
    
    else:
        return {}
    
    