from django.apps import AppConfig

from . import app_name, verbose_name

class Config(AppConfig):
    name = app_name
    verbose_name = verbose_name

    def ready(self):
        from . import signals  # noqa: F401
