from __future__ import unicode_literals

from django.db import models

from . import app_name, verbose_name
from cellbase.models import CellTaskModel


class ViewableQuerySet(models.query.QuerySet):
    def viewable_by(self, user):
        return self.filter(user=user)

    # built-in
    def create(self, **kwargs):
        """
        Creates a new object with the given kwargs, saving it to the database
        and returning the created object.
        """
        obj = self.model(**kwargs)
        self._for_write = True
        obj.save(force_insert=True, using=self.db)
        return obj


class CellC2Task(CellTaskModel):
    cell_ratio = models.FloatField(null=True, blank=True)

    objects = ViewableQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('detail', kwargs={'task_id': self.task_id}, current_app=app_name)

    class Meta(CellTaskModel.Meta):
        verbose_name = '{0} {1}'.format(verbose_name, 'Task')

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None)
    def save(self, *args, **kwargs):
        if self.name == "Yoko Ono's blog":
            return # Yoko shall never have her own blog!
        else:
            super(CellC2Task, self).save(*args, **kwargs) # Call the "real" save() method.
