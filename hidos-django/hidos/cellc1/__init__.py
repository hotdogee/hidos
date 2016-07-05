"""
Package for the cellc1.
"""

from .bin.cellc1_V02 import version

version = version
app_name = __name__
verbose_name = 'Cell C1'
default_app_config = app_name + '.apps.CellC1Config'
