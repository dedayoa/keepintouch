'''
Created on Aug 7, 2016

@author: Dayo
'''

import re
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from core.exceptions import MissingSMSRateError
from core.models import KITUBalance, FundsTransfer

from .models import SMSRateTable, EmailReport, SMSReport

from cacheops import cached_as
from country_dialcode.models import Prefix


# Courtesy Star2Billing #

class KITRateEngineA(object):

    def remove_prefix(self, phonenumber, removeprefix_list):
        # remove the prefix from phone number
        # @ removeprefix_list "+,0,00,000,0000,00000,011,55555,99999"
        #
        # clean : remove spaces
        removeprefix_list = removeprefix_list.strip(' \t\n\r')
        if removeprefix_list and len(removeprefix_list) > 0:
            removeprefix_list = removeprefix_list.split(',')
            removeprefix_list = sorted(removeprefix_list, key=len, reverse=True)
            for rprefix in removeprefix_list:
                rprefix = rprefix.strip(' \t\n\r')
                rprefix = re.sub("\+", "\\\+", rprefix)
                if rprefix and len(rprefix) > 0:
                    phonenumber = re.sub('^%s' % rprefix, '', phonenumber)
        return phonenumber
    
    def prefix_list_string(self, dest_number):
        """
        To return prefix string
        For Example :-
        dest_number = 34650XXXXXX
        prefix_string = (34650, 3465, 346, 34)
        >>> dest_number = 34650123456
        >>> prefix_list_string(dest_number)
        '34650, 3465, 346, 34'
        >>> dest_number = -34650123456
        >>> prefix_list_string(dest_number)
        False
        """
        # Extra number, this is used in case phonenumber is followed by chars
        # ie 34650123456*234
        dest_number = str(dest_number)
        if len(dest_number) > 0 and dest_number[0] == '+':
            dest_number = dest_number[1:]
    
        m = re.search('(\d*)', dest_number)
        dest_number = m.group(0)
        try:
            int(dest_number)
        except ValueError:
            return False
        prefix_range = range(settings.PREFIX_LIMIT_MIN, settings.PREFIX_LIMIT_MAX + 1)
        destination_prefix_list = ''
        for i in reversed(prefix_range):
            if i == settings.PREFIX_LIMIT_MIN:
                destination_prefix_list = destination_prefix_list + dest_number[0:i]
            else:
                destination_prefix_list = destination_prefix_list + dest_number[0:i] + ', '
        return str(destination_prefix_list)
    
    def get_country_id_prefix(self, prefix_list):
        @cached_as(Prefix, timeout=3600)
        def _get_country_id_prefix():
            """
            Get country_id and matched prefix from prefix_list
                @ return (country_id, prefix)
            In case of error or not found,
                @ return (None, None)
            """
            country_id = None
            prefix = None
            if not prefix_list:
                return (country_id, prefix)
        
            try:
                # get a list in numeric order (which is also length order)
                prefix_obj = Prefix.objects.filter(prefix__in=eval(prefix_list)).order_by('prefix')
                # find the longest prefix with a non-zero country_id
                for i in range(0, len(prefix_obj)):
                    if prefix_obj[i].country_id:
                        country_id = prefix_obj[i].country_id.id
                        prefix = prefix_obj[i].prefix
                return (country_id, prefix)
            except:
                return (country_id, prefix)
        
        return _get_country_id_prefix()
    
    
    def get_dialcode(self, destination_number, dialcode=""):
        """
        Retrieve the correct dialcode for a destination_number
        """

        if dialcode and len(dialcode) > 0:
            return dialcode
        else:
            # remove prefix
            sanitized_destination = self.remove_prefix(destination_number, settings.PREFIX_TO_IGNORE)
            prefix_list = self.prefix_list_string(sanitized_destination)
    
            if prefix_list and len(sanitized_destination) > settings.PN_MAX_DIGITS and not sanitized_destination[:1].isalpha():
                # International call
                (country_id, prefix_id) = self.get_country_id_prefix(prefix_list)
                dialcode = prefix_id
            else:
                dialcode = ''
        
        return dialcode
    
    
    def get_sms_cost_to_number(self, receiving_number):
        
        @cached_as(SMSRateTable, timeout=3600)        
        def _get_sms_units_cost():
            try:
                dc = self.get_dialcode(receiving_number)
                sms_u = SMSRateTable.objects.get(dialcode=dc)
                return sms_u.sms_units
            
            except ObjectDoesNotExist:
                raise MissingSMSRateError("SMS Rate Missing for %s"%dc)
        
        return _get_sms_units_cost()




def temp_log_to_db(m_type, **kwargs):
    
    if m_type == 'email':
        EmailReport.objects.create(
            to_email = kwargs['email_msg'][2],
            from_email = kwargs.get('sender_mail',''),
            status = 0,
            owner = kwargs.get('owner',''),
            email_message = {
                'title' : kwargs['email_msg'][0],
                'body' : kwargs['email_msg'][1]
                           },
            email_gateway = {
                'email_id' :'',
                'gateway_id' : '',
                'gateway_error_preamble' : kwargs.get('gw_err_preamble','')
                
                           }
        )
    
    elif m_type == 'sms':
        SMSReport.objects.create(
            to_phone = kwargs['sms_msg'][2],
            status = 0,
            gw_msg_id = kwargs.get('message_id', 0),
            owner = kwargs.get('owner',''),
            sms_message = {
                'sender_id' : kwargs['sms_msg'][0],
                'body' : kwargs['sms_msg'][1],
                'message_type' : '0'
                           },
            sms_gateway = {
                'gateway_id' : kwargs.get('gateway_id', ''),
                'gateway_error_code' : kwargs.get('message_err_code','')
                           },
        )
    
    

class BalanceTransferHelper(object):
    
    def __init__(self, from_user, to_user):
        self.from_user = from_user
        self.to_user = to_user
    
    @transaction.atomic   
    def credit(self, amount):
        # reduce from_user, increase to_user

        user = KITUBalance.objects.select_for_update().get(kit_user=self.to_user)
        admin = KITUBalance.objects.select_for_update().get(kit_user=self.from_user)
        
        user.user_balance = user.user_balance + amount
        admin.user_balance = admin.user_balance - amount
        
        user.save()
        admin.save()
        
        FundsTransfer.objects.create(
            from_user = admin.kit_user,
            to_user = user.kit_user,
            amount = amount,
            transaction_detail = {
                    'from_user_email' : admin.kit_user.user.email,
                    'to_user_email' : user.kit_user.user.email
                                  },
            created_by = admin.kit_user
        )
        
        return [admin.user_balance, user.user_balance]
    
    @transaction.atomic  
    def debit(self, amount):
        # reduce to_user, increase from_user
        user = KITUBalance.objects.select_for_update().get(kit_user=self.from_user)
        admin = KITUBalance.objects.select_for_update().get(kit_user=self.to_user)
        
        user.user_balance = user.user_balance - amount
        admin.user_balance = admin.user_balance + amount
        
        user.save()
        admin.save()
        
        FundsTransfer.objects.create(
            from_user = user.kit_user,
            to_user = admin.kit_user,
            amount = amount,
            transaction_detail = {
                    'from_user_email' : user.kit_user.user.email,
                    'to_user_email' : admin.kit_user.user.email
                                  },
            created_by = admin.kit_user
        )
        
        return [user.user_balance, admin.user_balance]
   
    