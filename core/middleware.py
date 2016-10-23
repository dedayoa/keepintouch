'''
Created on Aug 29, 2016

@author: Dayo
'''

import sys, re
from .views import validate_user_details
from gomez.views import SubscriptionExpired

from django.utils import timezone
from gomez.models import KITBilling

import pytz
from pytz.exceptions import UnknownTimeZoneError

class UserValidatedMiddleware(object):
    """
    Check if both phone and emails for user have been validated.
    If not, don't grant access to app
    """
    
    PIPTHRU_PATHS = (
        '/settings/account/user/send-verify-code/',
        '/settings/account/user/verify/',
        '/exit/'
                     )
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            if not (request.user.is_staff) :
                if request.user.kituser.email_validated and request.user.kituser.phone_validated:
                    return None
                elif request.path in self.PIPTHRU_PATHS:
                    return None
                return validate_user_details(request, *view_args, **view_kwargs)
        except AttributeError:
            # for AnonymousUser
            return None
        
        
class TimeZoneMiddleware(object):

    def process_request(self, request):
        try:
            if request.user.is_authenticated() and not request.user.is_staff:
                timezone.activate(pytz.timezone(str(request.user.kituser.timezone)))
            else:
                timezone.deactivate()
        except UnknownTimeZoneError:
            print("Error: Unknown Timezone")
            timezone.deactivate()
            
            
class SubscriptionExpiredMiddleware(object):
    
    PIPTHRU_PATHS = (
        '/order/start/',
        '/order/cart/',
        '/order/checkout/',
        '/exit/',
        '/order/[A-Z0-9]{10}/',
        '/order/[A-Z0-9]{10}/update/',
        '/order/[A-Z0-9]{10}/item/\d+/delete/'
        
    )
    
    def process_view(self,request, view_func, view_args, view_kwargs):
        try:
            # is not a staff, but is admin
            if not request.user.is_staff and request.user.kituser.is_admin:
                #if account is suspended (can be for other reasons) and next_due_date is in the past
                if request.user.kituser.kitbilling.next_due_date < timezone.now().date():
                    #if request.path in self.PIPTHRU_PATHS:
                    #    return None
                    for regexpr in self.PIPTHRU_PATHS:
                        if re.match(regexpr, request.path):
                            return None
                    return SubscriptionExpired.as_view()(request, *view_args, **view_kwargs)
                else:
                    return None
            else:
                return None
        except:
            print(sys.exc_info()[1])