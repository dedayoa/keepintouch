'''
Created on Nov 7, 2016

@author: Dayo
'''


import greenswitch
from uuid import uuid4
from django.conf import settings
import phonenumbers
from core.exceptions import InvalidPhoneNumberError, NotEnoughBalanceError, FailedDialOutError, MissingCallRateError
from gomez.helper import KITRateEngineA
from reportng.models import CallDetailReport
from .models import CallStatus


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
        crtn = KITRateEngineA().get_call_cost_to_number(self.caller)
        cetn = KITRateEngineA().get_call_cost_to_number(self.callee)
        
        return [crtn, cetn]

    def dial(self):
        dsb = 'sofia/internal/9'
        termination_gw = 'vgw.xoip.biz'
        intouch_fs_gw = '85.90.246.57'
        intouch_fs_gw_pwd = 'xHD192ESp'
        
        self.uuid = str(uuid4())
        
        data = {
                'uuid': self.uuid,
                'caller':self.caller[1:],
                'callee':self.callee[1:],
                'voipgw' : termination_gw,
                'dialstringbase' : dsb,
                'origcrcid' : self.orig_caller_cid,
                'origcecid' : self.orig_callee_cid
                }
        
        #af = '+OK Job-UUID: 8e44c73c-3c52-4573-b2a0-cc938678ee3d'
        
        try:
            fs = greenswitch.InboundESL(host=intouch_fs_gw, port=8021, password=intouch_fs_gw_pwd)
            fs.connect()
            r = fs.send('bgapi luarun callup.lua {uuid} {dialstringbase}{caller}@{voipgw} {dialstringbase}{callee}@{voipgw} {origcrcid} {origcecid}'.\
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
            cppm = self._check_call_can_be_made()
            CallDetailReport.objects.create(id=self.uuid,a_leg_per_min_call_price=cppm[0],\
                            b_leg_per_min_call_price=cppm[1], kituser_id = self.kuser.id, \
                            kitu_parent_id = self.kuser.parent.id                            
                            )
            
            job_uuid = self.dial()
            CallStatus.objects.create(id=job_uuid) #this should actually be in redis
            
        except InvalidPhoneNumberError as e:
            pass
        except NotEnoughBalanceError as e:
            pass
        except FailedDialOutError as e:
            pass
        except MissingCallRateError as e:
            pass
    