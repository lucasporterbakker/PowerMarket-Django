from django.apps import AppConfig


class LocationConfig(AppConfig):
    name = 'apps.location'

    def ready(self):
        import apps.location.signals
