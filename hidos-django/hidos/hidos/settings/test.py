"""
test settings

Uses SQLite unless DATABASE_URL is set (CI runs the suite against PostgreSQL).
"""
import tempfile

from .base import *  # noqa: F401,F403
from .base import PROJECT_ROOT, REST_FRAMEWORK, env, path

DEBUG = False

SECRET_KEY = 'django-insecure-test-key-only-for-the-test-suite'

ALLOWED_HOSTS = ['testserver', 'localhost']

DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///' + path.join(PROJECT_ROOT, 'test.sqlite3')),
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']  # fast tests only

MEDIA_ROOT = tempfile.mkdtemp(prefix='hidos-test-media-')
STATIC_ROOT = tempfile.mkdtemp(prefix='hidos-test-static-')

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_BROKER_URL = 'memory://'

SLACK_WEBHOOK_URL = ''

REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    **REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'],
    'anon': '10000/h',
    'register_view': '10000/h',
    'dj_rest_auth': '10000/h',
}
