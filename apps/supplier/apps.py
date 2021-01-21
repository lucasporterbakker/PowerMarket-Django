from django.apps import AppConfig


class SupplierConfig(AppConfig):
    name = 'apps.supplier'

    def ready(self):
        import apps.supplier.signals  # import all signals located in signals.py
