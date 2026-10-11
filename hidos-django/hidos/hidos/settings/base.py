"""
base settings

Every deployment-specific value is read from the environment (or from an
optional ``.env`` file next to ``manage.py``); see ``.env.example`` and the
README for the full list.
"""
from datetime import timedelta
from os import makedirs, path
from sys import platform

import environ
from kombu import Exchange, Queue

PROJECT_ROOT = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
REPO_ROOT = path.dirname(path.dirname(PROJECT_ROOT))

env = environ.Env()
if path.isfile(path.join(PROJECT_ROOT, '.env')):
    environ.Env.read_env(path.join(PROJECT_ROOT, '.env'))

DEBUG = env.bool('DJANGO_DEBUG', default=False)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['.hidos.io'])

ADMINS = [tuple(a.split(':', 1)) for a in env.list('DJANGO_ADMINS', default=[])]  # "Name:email,..."

MANAGERS = ADMINS

APPEND_SLASH = False

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = env('LOGIN_REDIRECT_URL', default='/')

# Make this unique, and don't share it with anybody.
# Required in production; local and test settings provide an insecure fallback.
SECRET_KEY = env('DJANGO_SECRET_KEY', default='')

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# e.g. DATABASE_URL=postgres://django:password@localhost:5432/django

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://django@localhost:5432/django'),
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password hashers
# bcrypt_sha256 stays the default so existing password hashes keep working.

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'users.User'

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

# Languages a user can pick in their profile (users.User.language)
LANGUAGES = [
    ('en', 'English'),
    ('zh-hant', 'Traditional Chinese'),
]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = env('TIME_ZONE', default='Asia/Taipei')

USE_I18N = True

USE_TZ = True

# File Permissions
# Shared by the web and worker processes, which may run as different users
# in the same group.
FILE_UPLOAD_PERMISSIONS = 0o664
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o775

# Largest single request body (uploads larger than this should use the
# chunked upload API, see fs.uploads)
DATA_UPLOAD_MAX_MEMORY_SIZE = env.int('DATA_UPLOAD_MAX_MEMORY_SIZE', default=10 * 1024 * 1024)

# Media files

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = env('MEDIA_ROOT', default=path.join(PROJECT_ROOT, 'media')).replace('\\', '/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
MEDIA_URL = env('MEDIA_URL', default='/media/')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Absolute path to the directory static files should be collected to.
STATIC_ROOT = env('STATIC_ROOT', default=path.join(PROJECT_ROOT, 'static')).replace('\\', '/')

# URL prefix for static files.
STATIC_URL = env('STATIC_URL', default='/static/')

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Application definition

SITE_ID = 1
# Written to the django_site row by app/migrations/0001_site_domain.py
SITE_DOMAIN = env('SITE_DOMAIN', default='hidos.io')
SITE_NAME = env('SITE_NAME', default='HiDOS')

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'corsheaders',
    'django_filters',
    'users.apps.Config',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'dj_rest_auth.registration',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'app.apps.AppConfig',
    'fs.apps.Config',
    'cell.apps.Config',
    'cella1.apps.Config',
    'cellc1.apps.Config',
    'cellc2.apps.Config',
    'cellm1.apps.Config',
    'cellm3.apps.Config',
    'celln1.apps.Config',
    'django.contrib.admin',
    'django.contrib.admindocs',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'hidos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            path.join(PROJECT_ROOT, 'templates').replace('\\', '/')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # `allauth` needs this from django
                'django.template.context_processors.request',
            ],
        },
    },
]

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'hidos.wsgi.application'


AUTHENTICATION_BACKENDS = (
    # Needed to login by email in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

# CORS (the Cell Cloud single page app is served from a different origin)
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOWED_ORIGIN_REGEXES = env.list('CORS_ALLOWED_ORIGIN_REGEXES', default=[
    r'^https://([\w-]+\.)*hidos\.io$',
])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['https://*.hidos.io'])

# Logging (#12)
# Everything goes to the console so `docker compose logs` and systemd see it.
# Set LOG_DIR to also keep rotating log files (django.log, celery.log).
LOG_LEVEL = env('LOG_LEVEL', default='INFO')
LOG_DIR = env('LOG_DIR', default='')


def build_logging(log_level, log_dir=''):
    logging = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'file': {
                'format': '%(asctime)s	%(name)s	%(levelname)s	%(message)s',
            },
            'console': {
                'format': '%(asctime)s %(levelname)s %(name)s: %(message)s',
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'console',
            },
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'mail_admins'],
                'level': log_level,
                'propagate': False,
            },
        },
    }
    web_loggers = ['hidos', 'app', 'fs', 'users']
    worker_loggers = ['celery', 'cell', 'cella1', 'cellc1', 'cellc2', 'cellm1', 'cellm3', 'celln1']
    for name in web_loggers + worker_loggers:
        logging['loggers'][name] = {'handlers': ['console'], 'level': log_level, 'propagate': False}
    if log_dir:
        makedirs(log_dir, exist_ok=True)
        for name, loggers in (('django', ['django'] + web_loggers), ('celery', worker_loggers)):
            logging['handlers'][name + '_log'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': path.join(log_dir, name + '.log'),
                'maxBytes': 1024 * 1024 * 100,  # 100 mb
                'backupCount': 5,
                'formatter': 'file',
            }
            for logger in loggers:
                logging['loggers'][logger]['handlers'].append(name + '_log')
    return logging


LOGGING = build_logging(LOG_LEVEL, LOG_DIR)

# Specify the default test runner.
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Rscript path (only used by the legacy R versions of the algorithms, kept in
# cellc2/bin/*.R and cellm1/bin/*.R; the current pipeline is pure Python)
R_SCRIPT = r"/usr/bin/Rscript"
FONT = 'DejaVuSerif-Italic.ttf'

if platform == 'win32':
    R_SCRIPT = r"C:\Program Files\R\R-3.2.4revised\bin\RScript.exe"
if platform == 'darwin':
    R_SCRIPT = r'/usr/local/bin/Rscript'
    FONT = '/Library/Fonts/Times New Roman.ttf'
R_SCRIPT = env('R_SCRIPT', default=R_SCRIPT)
FONT = env('FONT', default=FONT)


USE_CACHE = False

# Celery Settings (all read with the CELERY_ prefix, see hidos/celery.py)
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='amqp://guest:guest@localhost:5672//')
# Task state is stored on the Task rows, so a result backend is optional.
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=None)
CELERY_TASK_IGNORE_RESULT = CELERY_RESULT_BACKEND is None
CELERY_TASK_DEFAULT_QUEUE = 'cell'
CELERY_TASK_DEFAULT_EXCHANGE = 'hidos'
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'cell'
CELERY_TASK_QUEUES = (
    Queue('cell', Exchange('hidos'), routing_key='cell'),
)
CELERY_TASK_ROUTES = {
    '*.tasks.analysis': {
        'queue': 'cell',
        'routing_key': 'cell',
    },
}
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIME_ZONE
CELERY_WORKER_DISABLE_RATE_LIMITS = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
# Run tasks in-process (tests, or a quick demo without a broker)
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', default=False)
CELERY_TASK_EAGER_PROPAGATES = False

# Error reports from failed analysis tasks (#63); leave empty to disable.
SLACK_WEBHOOK_URL = env('SLACK_WEBHOOK_URL', default='')
SLACK_CHANNEL = env('SLACK_CHANNEL', default='#image-bug')

# Largest accepted image for an analysis task
TASK_UPLOAD_MAX_BYTES = env.int('TASK_UPLOAD_MAX_BYTES', default=200 * 1024 * 1024)

# Largest accepted profile image (#74)
PROFILE_IMAGE_MAX_BYTES = env.int('PROFILE_IMAGE_MAX_BYTES', default=2 * 1024 * 1024)

# Thumbnails generated for every uploaded image (#38), longest side in pixels
THUMBNAIL_SIZE = env.int('THUMBNAIL_SIZE', default=256)

# Chunked resumable uploads (#56); partial files are kept outside MEDIA_ROOT
CHUNKED_UPLOAD_ROOT = env('CHUNKED_UPLOAD_ROOT', default=path.join(PROJECT_ROOT, 'chunked_uploads'))
CHUNKED_UPLOAD_MAX_BYTES = env.int('CHUNKED_UPLOAD_MAX_BYTES', default=200 * 1024 * 1024)
CHUNKED_UPLOAD_EXPIRATION = timedelta(hours=env.int('CHUNKED_UPLOAD_EXPIRATION_HOURS', default=24))

# REST framework
# The fs and cell APIs are protected by tokens (#96): JWT from the login API,
# or DRF tokens created in the admin. Session authentication is only enabled
# when API_SESSION_AUTH is true (default in local settings) so the browsable
# API keeps working for developers.
API_SESSION_AUTH = env.bool('API_SESSION_AUTH', default=False)


def rest_authentication_classes(session_auth):
    classes = [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ]
    if session_auth:
        classes.append('rest_framework.authentication.SessionAuthentication')
    return tuple(classes)


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': rest_authentication_classes(API_SESSION_AUTH),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': env('THROTTLE_ANON', default='10/h'),
        'register_view': env('THROTTLE_REGISTER', default='2/h'),  # users.views.RegisterView
        'dj_rest_auth': env('THROTTLE_AUTH', default='60/h'),  # login, password reset, ...
        'task_submit': env('THROTTLE_TASK_SUBMIT', default='600/h'),  # new analysis tasks (#26)
        'upload_chunk': env('THROTTLE_UPLOAD_CHUNK', default='6000/h'),  # chunked uploads (#56)
    },
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': None,
}

# Email (EMAIL_URL, e.g. smtp+tls://user:password@smtp.example.com:587)
vars().update(env.email_url('EMAIL_URL', default='consolemail://'))
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='HiDOS Cell Cloud <noreply@hidos.io>')
SERVER_EMAIL = env('SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)

# allauth
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = env('ACCOUNT_EMAIL_VERIFICATION', default='mandatory')
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
# Social and local accounts are merged by email address (#67). Only emails the
# provider reports as verified are matched, and allauth wipes the local
# password when the local address was never verified (pre-account-takeover).
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time'],
        'EXCHANGE_TOKEN': True,
        # Facebook does not guarantee that the email is verified, so a
        # Facebook login is never merged into an existing local account.
        'VERIFIED_EMAIL': False,
    },
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'}
    }
}
# OAuth client credentials can be configured in the admin (Social applications)
# or with these environment variables.
for _provider in ('facebook', 'google'):
    _client_id = env('%s_CLIENT_ID' % _provider.upper(), default='')
    if _client_id:
        SOCIALACCOUNT_PROVIDERS[_provider]['APPS'] = [{
            'client_id': _client_id,
            'secret': env('%s_CLIENT_SECRET' % _provider.upper(), default=''),
        }]

# dj-rest-auth
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY': False,  # return the refresh token in the response body
    'SESSION_LOGIN': False,
    'LOGIN_SERIALIZER': 'users.serializers.LoginSerializer',
    'USER_DETAILS_SERIALIZER': 'users.serializers.UserDetailsSerializer',
    'JWT_SERIALIZER': 'users.serializers.JWTSerializer',
    'JWT_TOKEN_CLAIMS_SERIALIZER': 'users.serializers.TokenClaimsSerializer',
    'REGISTER_SERIALIZER': 'users.serializers.RegisterSerializer',
}

# djangorestframework-simplejwt (replaces djangorestframework-jwt)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=env.int('JWT_ACCESS_DAYS', default=7)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('JWT_REFRESH_DAYS', default=365)),
    # "JWT <token>" is what the djangorestframework-jwt era clients send
    'AUTH_HEADER_TYPES': ('JWT', 'Bearer'),
    'LEEWAY': 30,
}
