from django.apps import AppConfig


class ManagerConfig(AppConfig):
    name = 'apps.manager'

    def ready(self):
        import apps.manager.signals
