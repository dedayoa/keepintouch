'''
Created on Aug 18, 2016

@author: Dayo
'''


import arrow
from django.conf import settings


    
def date_of_dayindex_in_this_week(self):
    week_start = arrow.utcnow().floor('week')
    week_end = arrow.utcnow().ceil('week')
    for r in arrow.Arrow.range('week',week_start, week_end):
        if r.datetime.strftime("%w") == settings.RESET_SMS_DAY_TIME[0]:
            if r.datetime.strftime("%H") == settings.RESET_SMS_DAY_TIME[1]:
                return True


def process_monthly_sms_crediting(nowarg):
    if nowarg == arrow.utcnow().floor('month').date:
        try:
            pass
        except:
            pass
        
        
def process_reset_free_sms_weekly(nowarg):
    if date_of_dayindex_in_this_week():
        pass