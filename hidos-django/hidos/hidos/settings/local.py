"""
local settings
"""
from __future__ import absolute_import, unicode_literals

from .base import *

DEBUG = True

ALLOWED_HOSTS = ALLOWED_HOSTS + [
    '127.0.0.1',
    'localhost',
    '10.1.80.2',
    '10.0.20.86',
]

CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = (
    'localhost:8080',
    'localhost:8082',
    '10.1.80.2:8082',
    '10.0.20.86:8082',
    '.hotdogee.com',
    '.hidos.io',
)

INSTALLED_APPS = INSTALLED_APPS + [
    'corsheaders',
]

# EMAIL
DEFAULT_FROM_EMAIL = 'cellcloud@meridigen.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.meridigen.com'
EMAIL_HOST_USER = 'cellcloud'
EMAIL_HOST_PASSWORD = 'Meriuser123'
EMAIL_PORT = 587
# EMAIL_USE_TLS = True


# REST framework
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/h',
    'register_view':'20/h', # rest_auth.register.views.RegisterView
}