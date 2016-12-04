'''
Created on Jul 4, 2016

@author: Dayo
'''

#from redis import Redis
import django_rq
from rq_scheduler import Scheduler

from datetime import datetime

default_scheduler = django_rq.get_scheduler('default')


def run_schedules():
    # Delete any existing jobs in the scheduler when the app starts up
    
    # ### messaging is already doing this # ###
    
    #for job in default_scheduler.get_jobs():
    #    job.delete()
    
    

    default_scheduler.schedule(
        scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
        func='reportng.tasks.process_sms_deliveryreport_transaction',                   # Function to be queued
        #args=[arg1, arg2],             # Arguments passed into function when executed
        #kwargs={'foo': 'bar'},         # Keyword arguments passed into function when executed
        interval=120,              # Call every 2 minutes
        repeat=None                    # Repeat forever
    )
    
    default_scheduler.schedule(
        scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
        func='reportng.tasks.process_email_deliveryreport_transaction',                   # Function to be queued
        #args=[arg1, arg2],             # Arguments passed into function when executed
        #kwargs={'foo': 'bar'},         # Keyword arguments passed into function when executed
        interval=120,              # Call every 2 minutes
        repeat=None                    # Repeat forever
    )

    