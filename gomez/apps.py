from django.apps import AppConfig
from gomez.scheduler import run_schedules

class GomezConfig(AppConfig):
    name = 'gomez'


    def ready(self):
        run_schedules()