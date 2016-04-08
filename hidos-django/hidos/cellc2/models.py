from __future__ import unicode_literals

from django.db import models

from . import app_name, verbose_name
from cellbase.models import CellTaskModel


class CellC2Task(CellTaskModel):
    cell_ratio = models.FloatField()

    def get_absolute_url(self):
        return reverse('detail', args=[str(self.task_id)], current_app=app_name)

    class Meta(CellTaskModel.Meta):
        verbose_name = '{0} {1}'.format(verbose_name, 'Task')
