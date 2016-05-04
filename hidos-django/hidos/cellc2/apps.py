from __future__ import unicode_literals

from django.apps import AppConfig

from . import app_name, verbose_name

class CellC2Config(AppConfig):
    name = app_name
    verbose_name = verbose_name

#app_config_name = verbose_name.replace(' ', '') + 'Config'
#globals()[app_config_name] = type(app_config_name, (AppConfig,), dict(name = app_name, verbose_name = verbose_name))
#default_app_config = '.'.join((app_name, app_config_name))
