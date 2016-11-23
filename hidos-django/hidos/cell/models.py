from __future__ import absolute_import, unicode_literals
import re
import sys
import uuid
import hashlib
import imghdr
import stat as Perm
import posixpath as path
from os import makedirs, chmod

import cv2
import numpy as np

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import JSONField

from django_extensions.db.models import TimeStampedModel

from fs.models import File

from . import app_name, verbose_name, version

# Abstract model for a user submitted task
class Task(File):
    file_model = models.OneToOneField(File, models.CASCADE,
        parent_link=True, related_name='+') # explicit parent link with no related name
    status = models.CharField(max_length=32, default='queued') # queued, running, success, failed
    progress = models.FloatField(null=True, blank=True) # 0.00 to 1.00
    dequeued = models.DateTimeField(null=True, blank=True)
    finished = models.DateTimeField(null=True, blank=True)
    version = models.CharField(max_length=32)
    #cell_ratio = models.FloatField()

    class Meta(File.Meta):
        abstract = True


class ViewableQuerySet(models.query.QuerySet):

    def viewable_by(self, user):
        return self.filter(user=user)


class SingleImageUploadManager(models.Manager):

    def create(self, file, owner, folder, **kwargs): # QuerySet, file=file, owner=user
        """
        Create a CellTaskModel from a validated UploadedFile object
        """
        # app
        app_name = self.model.__module__.split('.')[0]
        app = sys.modules[app_name]
        print app_name, app

        # read to memory
        uploaded_file_data = file.read()

        # Generate task id
        m = hashlib.md5()
        m.update(app.version)
        m.update(owner.email) # if anonymous, username is ''
        m.update(uploaded_file_data)
        task_id = m.hexdigest()

        existing_queryset = self.filter(id=task_id)
        if existing_queryset.exists():
            # TODO: log existing
            return existing_queryset[0]

        # get image format
        image_type = imghdr.what('', uploaded_file_data)
        # path_prefix relative to MEDIA_ROOT
        path_prefix = path.join(app_name, 'task', task_id, task_id)
        # avoid exploits, don't any part of the user filename
        uploaded_image_path = path_prefix + '_uploaded.' + image_type
        result_image_path = path_prefix + '_result.' + image_type
        # jpg image for viewer
        uploaded_display_path = path_prefix + '_uploaded_display.jpg'
        result_display_path = path_prefix + '_result_display.jpg'

        # build data dictionary
        data = {
            'id': uuid.UUID(task_id),
            'name': file.name,
            'type': app_name,
            'version': app.version,
            'folder': folder,
            'status': 'queued',
            'progress': 0,
            'uploaded_filetype': image_type,
            'uploaded_image': uploaded_image_path,
            'result_image': result_image_path,
            'uploaded_display': uploaded_display_path,
            'result_display': result_display_path,
        }
        if not owner.is_anonymous:
            data['owner'] = owner
        obj = super(SingleImageUploadManager, self).create(**data)
        obj.content = obj

        chmod(path.dirname(path.join(settings.MEDIA_ROOT, app_name, 'task', task_id, task_id)), Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO)
        # save uploaded image data to file
        obj.uploaded_image.save(uploaded_image_path, file, save=False)

        # convert to jpeg for web display
        uploaded_image_array = np.asarray(bytearray(uploaded_file_data), dtype=np.uint8)
        flag, uploaded_display_array = cv2.imencode('.jpg', cv2.imdecode(uploaded_image_array, cv2.IMREAD_COLOR))
        obj.uploaded_display.save(uploaded_display_path, ContentFile(bytearray(uploaded_display_array)), save=False)

        # TODO: Make thumbnail

        # save to database
        obj.save()
        return obj

    # built-in
    # run create(file=UploadedFile object)
    # def create(self, **kwargs): # QuerySet, file=file;
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


# CellQ result model
class CellTask(Task):
    uploaded_filetype = models.CharField(max_length=10, blank=True)
    uploaded_image = models.ImageField(max_length=255, blank=True)
    result_image = models.ImageField(max_length=255, blank=True)
    uploaded_display = models.ImageField(max_length=255, blank=True)
    result_display = models.ImageField(max_length=255, blank=True)
    result = JSONField(default=dict, blank=True) # requires postgres
    error = models.TextField(blank=True)

    objects = SingleImageUploadManager.from_queryset(ViewableQuerySet)()

    class Meta(Task.Meta):
        abstract = True

# TODO: Permissions class for sharing
