'''
Created on Aug 29, 2016

@author: Dayo
'''

from .views import validate_user_details

class UserValidatedMiddleware(object):
    """
    Check if both phone and emails for user have been validated.
    If not, don't grant access to app
    """
    
    PIPTHRU_PATHS = (
        '/settings/account/user/send-verify-code/',
        '/settings/account/user/verify/'  
                     )
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            if request.user.kituser.email_validated and request.user.kituser.phone_validated:
                return None
            elif request.path in self.PIPTHRU_PATHS:
                return None
            return validate_user_details(request, *view_args, **view_kwargs)
        except AttributeError:
            return None