'''
Created on Aug 20, 2016

@author: Dayo
'''


class FailedSendingMessageError(Exception):
    # critical failure e.g admin trying to send message
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)
    
class IsNotActiveError(Exception):
    # user is not active or parent is not active
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)
    
class NoActiveSubscriptionError(Exception):
    # no active or valid subscription
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)
    
class NotEnoughBalanceError(Exception):
    # balance not enogh error
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)
    
class SMSGatewayError(Exception):
    # balance not enogh error
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)
    

class MissingSMSRateError(Exception):
    # balance not enogh error
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)
    
