"""
Package for the cellc1.
"""

from .bin.cellm3_V02 import version


version = version
app_name = __name__
verbose_name = 'Cell M3'
default_app_config = app_name + '.apps.CellM3Config'
