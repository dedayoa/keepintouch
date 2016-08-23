from django.apps import AppConfig

from messaging.scheduler import run_schedules


class MessagingConfig(AppConfig):
    name = 'messaging'


    def ready(self):
        run_schedules()