from __future__ import unicode_literals
import hashlib

from django.db import models

from . import app_name, verbose_name, version
from cellbase.models import CellTaskModel


class ViewableQuerySet(models.query.QuerySet):

    def viewable_by(self, user):
        return self.filter(user=user)


class SingleImageUploadManager(models.Manager):

    def create(self, **kwargs): # QuerySet, file=file, user=user
        """
        Create a CellTaskModel from a validated UploadedFile object
        """
        # Generate task id
        m = hashlib.md5()
        m.update(version)
        m.update(user.username) # if anonymous, username is ''
        for chunk in file.chunks():
            m.update(chunk)
        task_id = m.hexdigest()

        # Make input jpg
        # Make thumbnail

        # Build data dictionary
        data = {
            task_id: task_id,
            version: version,
            user_filename: file.name,
            result_status: 'queued',
            user: user
        }
        return super(SingleImageUploadManager, self).create(**data)

    # built-in
    # run create(file=UploadedFile object)
    # def create(self, **kwargs): # QuerySet, file=file
    #     """
    #     Creates a new object with the given kwargs, saving it to the database
    #     and returning the created object.
    #     """
    #     obj = self.model(**kwargs)
    #     self._for_write = True
    #     obj.save(force_insert=True, using=self.db)
    #     return obj

    # @classmethod
    # def from_queryset(cls, queryset_class, class_name=None): # BaseManager
    #     if class_name is None:
    #         class_name = '%sFrom%s' % (cls.__name__, queryset_class.__name__) # ManagerFromQuerySet
    #     class_dict = {
    #         '_queryset_class': queryset_class,
    #     }
    #     class_dict.update(cls._get_queryset_methods(queryset_class))
    #     return type(class_name, (cls,), class_dict)


class CellC2Task(CellTaskModel):
    cell_ratio = models.FloatField(null=True, blank=True)

    objects = SingleImageUploadManager.from_queryset(ViewableQuerySet)

    def get_absolute_url(self):
        return reverse('detail', kwargs={'task_id': self.task_id}, current_app=app_name)

    class Meta(CellTaskModel.Meta):
        verbose_name = '{0} {1}'.format(verbose_name, 'Task')

    def run_delay(self):
        # Generate args_list and path_prefix
        run_image_analysis_task.delay(task_id, args_list, path_prefix)

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None)
    # def save(self, *args, **kwargs):
    #     if self.name == "Yoko Ono's blog":
    #         return # Yoko shall never have her own blog!
    #     else:
    #         super(CellC2Task, self).save(*args, **kwargs) # Call the "real" save() method.
