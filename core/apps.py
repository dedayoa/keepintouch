from django.apps import AppConfig
from watson import search as watson


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        import core.signals
        Contact = self.get_model('Contact')
        watson.register(Contact, fields=("first_name", "last_name","email","phone",))