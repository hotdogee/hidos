from __future__ import absolute_import, unicode_literals
import sys
import hashlib
import imghdr
import stat as Perm
from os import path, makedirs, chmod

from PIL import Image

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from django_extensions.db.models import TimeStampedModel

from . import app_name, verbose_name, version

class Folder(TimeStampedModel):
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255) # display name
    owner = models.ForeignKey(User, models.CASCADE)
    parent_folder = models.ForeignKey('self', models.CASCADE, related_name='child_folders')


# Abstract model for a user submitted task
class TaskModel(TimeStampedModel):
    task_id = models.CharField(max_length=32, primary_key=True) # ex. 128c8661c25d45b8-9ca7809a09619db9
    status = models.CharField(max_length=32, default='queued') # queued, running, success, failed
    dequeued = models.DateTimeField(null=True, blank=True)
    finished = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    parent_folder = models.ForeignKey(Folder, models.SET_NULL, null=True, blank=True)
    version = models.CharField(max_length=32)
    #cell_ratio = models.FloatField()

    def __unicode__(self):
        return self.task_id

    class Meta(TimeStampedModel.Meta):
        abstract = True


class ViewableQuerySet(models.query.QuerySet):

    def viewable_by(self, user):
        return self.filter(user=user)


class SingleImageUploadManager(models.Manager):

    def create(self, file, user, **kwargs): # QuerySet, file=file, user=user
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
        m.update(user.username) # if anonymous, username is ''
        m.update(uploaded_file_data)
        task_id = m.hexdigest()

        existing_queryset = self.filter(task_id=task_id)
        if existing_queryset.exists():
            return existing_queryset[0]

        # get image format
        image_type = imghdr.what('', uploaded_file_data)
        # Generate args_list and path_prefix
        path_prefix = path.join(settings.MEDIA_ROOT, app_name, 'task', task_id, task_id)
        # avoid exploits, don't any part of the user filename
        uploaded_image_path = path_prefix + '_uploaded.' + image_type
        # jpg image for viewer
        input_image_viewer_path = path_prefix + '_in.jpg'


        # create directory
        if not path.exists(path.dirname(path_prefix)):
            makedirs(path.dirname(path_prefix))
        # ensure the standalone dequeuing process can open files in the directory
        chmod(path.dirname(path_prefix), Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO)

        # write original image data to file
        with open(uploaded_image_path, 'wb') as uploaded_image_f:
            uploaded_image_f.write(uploaded_file_data)
        chmod(uploaded_image_path, Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO)

        # convert to jpeg for web display
        p = Image.open(uploaded_image_path)
        if p.mode.split(';')[1:2] == ['16']:
            p = p.point(lambda x: x*(float(1)/256))
        if p.mode != 'RGB':
            p = p.convert('RGB')
        p.save(input_image_viewer_path)
        chmod(input_image_viewer_path, Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO)

        # Make input jpg
        # Make thumbnail

        # Build data dictionary
        data = {
            'task_id': task_id,
            'version': app.version,
            'uploaded_filename': file.name,
            'uploaded_filetype': image_type,
            'status': 'queued',
        }
        if user.username:
            data['user'] = user
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


# CellQ result model
class CellTaskModel(TaskModel):
    # user file name
    uploaded_filename = models.CharField(max_length=255) # ext3 max filename = 255
    # uploaded image file type
    uploaded_filetype = models.CharField(max_length=10)
    stdout = models.TextField(blank=True)
    stderr = models.TextField(blank=True)

    objects = SingleImageUploadManager.from_queryset(ViewableQuerySet)()

    def __unicode__(self):
        return '{0} ({1})'.format(self.uploaded_filename, self.task_id[:6])

    class Meta(TaskModel.Meta):
        abstract = True

# TODO: Permissions class for sharing
