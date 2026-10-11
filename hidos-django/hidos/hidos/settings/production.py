"""
production settings
"""
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import SECRET_KEY, env

if not SECRET_KEY:
    raise ImproperlyConfigured('Set the DJANGO_SECRET_KEY environment variable.')
# Django's security.W009 check, as an error: the key signs the JWTs and keys
# the task ids in the public media URLs, so a placeholder must not pass.
if len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 5 or SECRET_KEY.startswith('django-insecure-'):
    raise ImproperlyConfigured(
        'DJANGO_SECRET_KEY must be at least 50 random characters, e.g. '
        'python -c "import secrets; print(secrets.token_urlsafe(50))"')

# TLS is terminated by the reverse proxy (tools/nginx), which sets X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    # no manifest: the vendored 2016 static files (UTF-16 IntelliSense files,
    # CSS referencing missing fonts) can't be post-processed
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}
