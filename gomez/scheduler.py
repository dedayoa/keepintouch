'''
Created on Aug 18, 2016

@author: Dayo
'''
#from redis import Redis
import django_rq
from rq_scheduler import Scheduler
import arrow

from datetime import datetime

default_scheduler = django_rq.get_scheduler('default')



def run_schedules():
    # Delete any existing jobs in the scheduler when the app starts up
    for job in default_scheduler.get_jobs():
        job.delete()
    
    
    # User SMS Balance crediting
    # Run every month
    job86p4k = default_scheduler.schedule(
        scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
        func='gomez.tasks.process_monthly_sms_crediting',                     # Function to be queued
        args=[datetime.utcnow().date()],             # Arguments passed into function when executed
        #kwargs={'foo': 'bar'},         # Keyword arguments passed into function when executed
        interval=86400,              # Call once a day
        repeat=None                 # Repeat forever
    )
    
    
    # Public Event Scheduler
    # Run every 1 hour
    job_36k = default_scheduler.schedule(
        scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
        func='gomez.tasks.process_reset_free_sms_weekly',
        interval=3600, 
        repeat=None
    )
    

    
    return (job86p4k, job_36k)
    