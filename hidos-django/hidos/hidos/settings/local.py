"""
local settings
"""
from __future__ import absolute_import, unicode_literals

from .base import *

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# REST framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/h',
        'register_view':'20/h', # rest_auth.register.views.RegisterView
    }
}