"""
local settings
"""
from .base import *  # noqa: F401,F403
from .base import (
    ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, LOG_LEVEL, REPO_ROOT, REST_FRAMEWORK, build_logging, env, path,
    rest_authentication_classes,
)

DEBUG = env.bool('DJANGO_DEBUG', default=True)

# Development only; production requires DJANGO_SECRET_KEY.
SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-local-development-key-do-not-use-in-production')

ALLOWED_HOSTS = ALLOWED_HOSTS + [
    '127.0.0.1',
    'localhost',
]

CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS + [
    'http://localhost:8080',
    'http://localhost:8082',
]

CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Browsable API with session login for development
API_SESSION_AUTH = env.bool('API_SESSION_AUTH', default=True)
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = rest_authentication_classes(API_SESSION_AUTH)

# REST framework
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    **REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'],
    'anon': '100/h',
    'register_view': '20/h',  # users.views.RegisterView
}

# Keep the old ../../log/*.log files during development
LOG_DIR = env('LOG_DIR', default=path.join(REPO_ROOT, 'log'))
LOGGING = build_logging(LOG_LEVEL, LOG_DIR)
