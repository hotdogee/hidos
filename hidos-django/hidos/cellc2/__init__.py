"""
Package for the cellc2.
"""

from .bin.cellc2_V07 import version

version = version
app_name = __name__
verbose_name = 'Cell C2'
default_app_config = app_name + '.apps.CellC2Config'
