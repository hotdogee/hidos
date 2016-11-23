"""
local settings
"""
from __future__ import absolute_import, unicode_literals

from .base import *

DEBUG = True

ALLOWED_HOSTS = ALLOWED_HOSTS + [
    '127.0.0.1',
    'localhost'
]

CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = (
    'localhost:8080',
    'localhost:8082',
    '.hotdogee.com',
    '.hidos.io',
)

INSTALLED_APPS = INSTALLED_APPS + [
    'corsheaders',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# REST framework
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/h',
    'register_view':'20/h', # rest_auth.register.views.RegisterView
}