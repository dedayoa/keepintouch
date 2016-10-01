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
    #for job in default_scheduler.get_jobs():
    #    job.delete()
    
    
    # Private Event Scheduler
    # Run every 1 hour
    default_scheduler.schedule(
        scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
        func='messaging.tasks.process_private_anniversary',                     # Function to be queued
        #args=[arg1, arg2],             # Arguments passed into function when executed
        #kwargs={'foo': 'bar'},         # Keyword arguments passed into function when executed
        interval=3600,              # Call every 1 hour
        repeat=None                    # Repeat forever
    )
    
    
    # Public Event Scheduler
    # Run every 4 hours
    default_scheduler.schedule(
        scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
        func='messaging.tasks.process_public_anniversary',                     # Function to be queued
        #args=[arg1, arg2],             # Arguments passed into function when executed
        #kwargs={'foo': 'bar'},         # Keyword arguments passed into function when executed
        interval=14400,              # Call every 4 hours
        repeat=None                      # Repeat forever
    )
    
    # Public Event Scheduler
    # Run every 5 minutes
    default_scheduler.schedule(
        scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
        func='messaging.tasks.process_onetime_event',                     # Function to be queued
        #args=[arg1, arg2],             # Arguments passed into function when executed
        #kwargs={'foo': 'bar'},         # Keyword arguments passed into function when executed
        interval=60,                  # Call every 3 minutes
        repeat=None                      # Repeat forever
    )
    
    # Reminder Messages Scheduler
    # Run once a day
    default_scheduler.schedule(
        scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
        func='messaging.tasks.process_reminder_event',                     # Function to be queued
        #args=[arg1, arg2],             # Arguments passed into function when executed
        #kwargs={'foo': 'bar'},         # Keyword arguments passed into function when executed
        interval=86400,                  # Call every 5 minutes
        repeat=None                      # Repeat forever
    )
    
    