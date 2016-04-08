from __future__ import unicode_literals

from django.db import models

from . import app_name, verbose_name
from cellbase.models import CellTaskModel


class ViewableQuerySet(models.query.QuerySet):
    def viewable_by(self, user):
        return self.filter(user=user)


class CellC2Task(CellTaskModel):
    cell_ratio = models.FloatField(null=True, blank=True)

    objects = ViewableQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('detail', kwargs={'task_id': self.task_id}, current_app=app_name)

    class Meta(CellTaskModel.Meta):
        verbose_name = '{0} {1}'.format(verbose_name, 'Task')
