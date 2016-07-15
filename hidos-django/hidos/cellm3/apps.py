from __future__ import unicode_literals

from django.apps import AppConfig

from . import app_name, verbose_name


class Config(AppConfig):
    name = app_name
    verbose_name = verbose_name
