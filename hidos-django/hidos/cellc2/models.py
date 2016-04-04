from __future__ import unicode_literals

from django.db import models

from cellbase.models import CellTaskModel


class CellC2Task(CellTaskModel):
    #cell_ratio = models.FloatField()


    def get_absolute_url(self):
        return reverse('cellc2:detail', args=[str(self.task_id)])

    class Meta(CellTaskModel.Meta):
        verbose_name = 'Cell C2 Task'
