from django.apps import AppConfig


class SupportConfig(AppConfig):
    name = "apps.support"
    verbose_name = "Support"

    def ready(self):
        import apps.support.signals  # import all signals located in signals.py