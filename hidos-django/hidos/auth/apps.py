from __future__ import unicode_literals
from . import app_name, verbose_name
from django.apps import AppConfig


class Config(AppConfig):
    name = app_name
    verbose_name = verbose_name
