from django.apps import AppConfig

from datetime import datetime
import django_rq
from rq_scheduler import Scheduler

#from .tasks import process_private_anniversary, process_public_anniversary, process_onetime_event


class MessagingConfig(AppConfig):
    name = 'messaging'


    def ready(self):
        default_scheduler = django_rq.get_scheduler('default')
        
        # Delete any existing jobs in the scheduler when the app starts up
        for job in default_scheduler.get_jobs():
            job.delete()
        
        
        # Private Event Scheduler
        # Run every 1 hour
        default_scheduler.schedule(
            scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
            func='messaging.tasks.process_private_anniversary',                     # Function to be queued
            #args=[arg1, arg2],             # Arguments passed into function when executed
            #kwargs={'foo': 'bar'},         # Keyword arguments passed into function when executed
            interval=1*60*60,              # Call every 1 hour
            repeat=None                    # Repeat forever
        )
        
        
        # Public Event Scheduler
        # Run every 4 hour
        default_scheduler.schedule(
            scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
            func='messaging.tasks.process_public_anniversary',                     # Function to be queued
            #args=[arg1, arg2],             # Arguments passed into function when executed
            #kwargs={'foo': 'bar'},         # Keyword arguments passed into function when executed
            interval=4*60*60,              # Call every 4 hours
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