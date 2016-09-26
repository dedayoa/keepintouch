'''
Created on Aug 29, 2016

@author: Dayo
'''

from .views import validate_user_details

from django.utils import timezone

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