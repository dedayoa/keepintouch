'''
Created on Nov 7, 2016

@author: Dayo
'''


import greenswitch
from decimal import Decimal, ROUND_DOWN
from uuid import uuid4
from django.conf import settings
import phonenumbers
from core.exceptions import InvalidPhoneNumberError, NotEnoughBalanceError, FailedDialOutError, MissingCallRateError
from gomez.helper import KITRateEngineA
from reportng.models import CallDetailReport
from .models import CallStatus
import json


class CallHelper():
    
    def __init__(self, callee, kuser):
        self.callee = callee #e164 format
        self.orig_caller_cid = kuser.parent.kitsystem.did_number
        
        if kuser.kitsystem.user_phone_as_callerid == False:            
            self.orig_callee_cid = kuser.parent.kitsystem.did_number
        else:
            self.orig_callee_cid = (kuser.phone_number.as_e164)[1:]
        
        self.caller = kuser.phone_number.as_e164 #e164 format
        self.kuser = kuser
        self.uuid = ''
    
    def _check_call_can_be_made(self):
    
        # check that phone numbers are valid        
        if not phonenumbers.is_valid_number(phonenumbers.parse(self.callee)):
            raise InvalidPhoneNumberError("Callee Number, %s is Not a Valid Phone Number"%str(self.callee))
        
        if not phonenumbers.is_valid_number(phonenumbers.parse(self.caller)):
            raise InvalidPhoneNumberError("Caller Number, %s is Not a Valid Phone Number"%str(self.caller))
        
        # check that user has balance 
        user_balance = self.kuser.kitubalance.user_balance        
        if user_balance <= 0:
            raise NotEnoughBalanceError("Not enough balance to make call")
        
        # check and get the rate of the call
        self.crtn = KITRateEngineA().get_call_cost_to_number(self.caller)
        self.cetn = KITRateEngineA().get_call_cost_to_number(self.callee)
    
    
    def _get_call_duration(self):
        user_balance = self.kuser.kitubalance.user_balance
        # we assume the call will complete
        both_legs_call_cost_per_min = self.crtn + self.cetn
        
        return ((user_balance/both_legs_call_cost_per_min)*60).quantize(Decimal('1'), rounding=ROUND_DOWN)
        

    def dial(self):
        dsb = 'sofia/internal/9'
        termination_gw = 'vgw.xoip.biz'
        intouch_fs_gw = '85.90.246.57'
        intouch_fs_gw_pwd = 'xHD192ESp'
        
        self.uuid = str(uuid4())
        
        calltout = self._get_call_duration()
        
        data = {
                'uuid': self.uuid,
                'caller':self.caller[1:],
                'callee':self.callee[1:],
                'voipgw' : termination_gw,
                'dialstringbase' : dsb,
                'origcrcid' : self.orig_caller_cid,
                'origcecid' : self.orig_callee_cid,
                'calltimeout' : calltout
                }
        
        #af = '+OK Job-UUID: 8e44c73c-3c52-4573-b2a0-cc938678ee3d'
        
        try:
            fs = greenswitch.InboundESL(host=intouch_fs_gw, port=8021, password=intouch_fs_gw_pwd)
            fs.connect()
            r = fs.send('bgapi luarun callup.lua {uuid} {calltimeout} {dialstringbase}{caller}@{voipgw} {dialstringbase}{callee}@{voipgw} {origcrcid} {origcecid}'.\
                        format(**data))
            
            
            if r.data[0:3] == '+OK':
                jobuuid = r.data.split(':')[1].strip()
                return jobuuid
            else:
                raise FailedDialOutError()
        except AttributeError:
            print("Something happened")
            
            
    def make_my_call(self):
        
        try:
            self._check_call_can_be_made()            
            job_uuid = self.dial()
            CallDetailReport.objects.create(id=self.uuid,a_leg_per_min_call_price=self.crtn,\
                            b_leg_per_min_call_price=self.cetn, kituser_id = self.kuser.id, \
                            kitu_parent_id = self.kuser.parent.id                            
                            )
            CallStatus.objects.create(job_uuid=job_uuid) #this should actually be in redis
            return [0,job_uuid]
            
        except InvalidPhoneNumberError as e:
            return [1,e.message]
        except NotEnoughBalanceError as e:
            return [3,e.message]
        except FailedDialOutError as e:
            return [5,e.message]
        except MissingCallRateError as e:
            return [9,e.message]
    
    
def return_all_level_err(message):
    return json.dumps({'__all__': [{'message' : message}]}
                                            )