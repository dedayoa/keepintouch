'''
Created on Jun 15, 2016

@author: Dayo
'''

from django_cron import CronJobBase, Schedule


class PrivateEventCronJob(CronJobBase):
    
    RUN_EVERY_MINS = 60
    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'messaging.private_event_cron_job'
    
    def do(self):
        pass
    
    
class PublicEventCronJob(CronJobBase):
    
    RUN_EVERY_MINS = 240
    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'messaging.public_event_cron_job'
    
    def do(self):
        pass
    
    
class MessagingCronJob(CronJobBase):
    
    RUN_EVERY_MINS = 5
    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'messaging.messaging_cron_job'
    
    def do(self):
        pass
    

class GetSMSDeliveryStatusCronJob(CronJobBase):
    
    RUN_EVERY_MINS = 10
    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'messaging.get_sms_delivery_status_cron_job'
    
    def do(self):
        pass
      
    
