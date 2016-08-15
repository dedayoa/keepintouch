from django.apps import AppConfig

from datetime import datetime
import django_rq
from rq_scheduler import Scheduler

from messaging.scheduler import run_schedules


class MessagingConfig(AppConfig):
    name = 'messaging'


    def ready(self):
        run_schedules()