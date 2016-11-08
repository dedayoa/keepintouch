'''
Created on Aug 18, 2016

@author: Dayo
'''


import arrow, time
import logging
from messaging.helper import assemble_message

from django.conf import settings
from django.db import IntegrityError

from core.models import KITActivationCode, KITUser
from gomez.helper import BalanceTransferHelper


logger = logging.getLogger(__name__)
    
def date_of_dayindex_in_this_week(self):
    week_start = arrow.utcnow().floor('week')
    week_end = arrow.utcnow().ceil('week')
    for r in arrow.Arrow.range('week',week_start, week_end):
        if r.datetime.strftime("%w") == settings.RESET_SMS_DAY_TIME[0]:
            if r.datetime.strftime("%H") == settings.RESET_SMS_DAY_TIME[1]:
                return True

'''
def process_monthly_sms_crediting():
    if arrow.utcnow().date().day == 1:
        try:
            # credit each active admin with her monthly SMS credit.
            for kadmin in KITUser.objects.filter(is_admin=True, user__is_active=True).iterator():
                if hasattr(kadmin.kitbilling.service_plan, 'sms_unit_bundle'):
                    kadmin_monthly_credit = kadmin.kitbilling.service_plan.sms_unit_bundle
                    
                    # kadmin.kitubalance.sms_balance = kadmin.kitubalance.sms_balance + kadmin_monthly_credit
                    # transfer credit from system to user
                    ksystem = KITUser.objects.get(id=settings.SYSTEM_KITUSER_ID)
                    
                    sth = BalanceTransferHelper(ksystem, kadmin)
                    result = sth.debit(kadmin_monthly_credit)
                    # @todo: send email to user to inform her of this crediting
                
        except IntegrityError:
            logger.error("System has run out of credit!")
            time.sleep(3600)
            logger.info("Retrying to process crediting of monthly SMS")
            process_monthly_sms_crediting()
    
'''
               
def expire_validation_code():
    
    result = KITActivationCode.objects.filter(created__lte = arrow.utcnow().replace(hours=-24).datetime).update(expired=True)
    logger.info("%s activation codes expired"%result)
    

    
    