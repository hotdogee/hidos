from __future__ import absolute_import, unicode_literals
from os import path

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from cell.models import File, CellTask, ViewableQuerySet, SingleImageUploadManager
from .tasks import analysis
from . import app_name, verbose_name, version

class Task(CellTask):

    # def get_absolute_url(self):
    #     return reverse(app_name + ':detail', kwargs={'id': self.id.hex}, current_app=app_name)

    class Meta(CellTask.Meta):
        verbose_name = '{0} {1}'.format(verbose_name, 'Task')

    def enqueue(self):
        """Insert task into task queue
        """
        analysis.delay(self.id.hex)
