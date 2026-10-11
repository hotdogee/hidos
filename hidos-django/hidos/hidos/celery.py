import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hidos.settings.local')

app = Celery('hidos')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
# All celery settings are read from Django settings with a CELERY_ prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

