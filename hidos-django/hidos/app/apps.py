from django.apps import AppConfig as djangoAppConfig

class AppConfig(djangoAppConfig):
    name = 'app'
    verbose_name = 'app'