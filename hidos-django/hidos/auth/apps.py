from __future__ import unicode_literals

from django.conf import settings
from django.apps import AppConfig

from . import app_name, verbose_name

project_name = settings.ROOT_URLCONF.split('.')[0]

class Config(AppConfig):
    name = app_name
    verbose_name = verbose_name
    label = '_'.join([project_name, app_name])
