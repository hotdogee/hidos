from __future__ import absolute_import, unicode_literals
from os import path

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from cell.models import File, CellTask, ViewableQuerySet, SingleImageUploadManager
from .tasks import process_image
from . import app_name, verbose_name, version

class Task(CellTask):
    cell_ratio = models.FloatField(null=True, blank=True)
    count_min = models.FloatField(null=True, blank=True)
    count_max = models.FloatField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('c2:detail', kwargs={'id': self.id}, current_app=app_name)

    class Meta(CellTask.Meta):
        verbose_name = '{0} {1}'.format(verbose_name, 'Task')

    def enqueue(self):
        """Insert task into task queue
        """
        process_image.delay(self.id)

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None)
    # def save(self, *args, **kwargs):
    #     if self.name == "Yoko Ono's blog":
    #         return # Yoko shall never have her own blog!
    #     else:
    #         super(CellC2Task, self).save(*args, **kwargs) # Call the "real" save() method.
