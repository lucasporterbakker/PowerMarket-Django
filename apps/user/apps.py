from django.apps import AppConfig


class UserConfig(AppConfig):
    name = "apps.user"
    verbose_name = "User"

    def ready(self):
        import apps.user.signals  # import all signals located in signals.py
