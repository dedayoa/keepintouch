from django.apps import AppConfig

from reportng.scheduler import run_schedules


class ReportngConfig(AppConfig):
    name = 'reportng'


    def ready(self):
        import reportng.signals
        run_schedules()