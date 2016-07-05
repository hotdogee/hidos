"""
Package for the cellc1.
"""
from .bin.cella_V02 import version


version = version
app_name = __name__
verbose_name = 'Cell A'
default_app_config = app_name + '.apps.CellAConfig'
