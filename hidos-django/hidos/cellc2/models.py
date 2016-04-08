from __future__ import unicode_literals

from django.db import models

from . import app_name, verbose_name
from cellbase.models import CellTaskModel


class CellC2Task(CellTaskModel):
    cell_ratio = models.FloatField(blank=True)

    def get_absolute_url(self):
        return reverse('detail', kwargs={'task_id': self.task_id}, current_app=app_name)

    class Meta(CellTaskModel.Meta):
        verbose_name = '{0} {1}'.format(verbose_name, 'Task')
