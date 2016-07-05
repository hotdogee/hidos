"""
Package for the cellc1.
"""
from .bin.cellm1_V02 import version


version = version
app_name = __name__
verbose_name = 'Cell M1'
default_app_config = app_name + '.apps.CellM1Config'
