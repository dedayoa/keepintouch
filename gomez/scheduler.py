'''
Created on Aug 18, 2016

@author: Dayo
'''
#from redis import Redis
import django_rq
from rq_scheduler import Scheduler
#import arrow

from datetime import datetime

default_scheduler = django_rq.get_scheduler('default')



def run_schedules():
    # Delete any existing jobs in the scheduler when the app starts up
    #for job in default_scheduler.get_jobs():
    #    job.delete()
    # expire verification codes that have been created over 24hours
    
    arg1 = default_scheduler.schedule(
        scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
        func='gomez.tasks.expire_validation_code',
        interval=3600, 
        repeat=None
    )    
    
    # User SMS Balance crediting
    # Run every month
    arg2 = default_scheduler.schedule(
        #scheduled_time=arrow.utcnow().ceil('day').replace(seconds=+1).datetime, # Time for first execution, in UTC timezone
        scheduled_time=datetime.utcnow().replace(day=datetime.utcnow().day+1, hour=0, minute=0, second=0),
        func='gomez.tasks.process_monthly_sms_crediting',                     # Function to be queued
        #kwargs={'foo': 'bar'},         # Keyword arguments passed into function when executed
        interval=86400,              # Call once a day
        repeat=None                  # Repeat forever
    )
    
    return (arg1, arg2)