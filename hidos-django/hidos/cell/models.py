import hmac
import io
import logging
import sys
import uuid
import posixpath as path

import cv2
import numpy as np
from PIL import Image

from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile

from fs.models import File

logger = logging.getLogger(__name__)

# Pillow format name -> file extension used for the stored upload
# (the same names imghdr returned before Python 3.13 removed it)
IMAGE_TYPES = {'mpo': 'jpeg'}


def image_type_of(data):
    """'jpeg', 'png', 'tiff', ... for the image bytes `data`"""
    with Image.open(io.BytesIO(data)) as img:
        fmt = (img.format or 'bin').lower()
    return IMAGE_TYPES.get(fmt, fmt)


def display_jpeg(data):
    """8-bit JPEG version of an uploaded image for web display"""
    decoded = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if decoded is not None:
        flag, encoded = cv2.imencode('.jpg', decoded)
        if flag:
            return encoded.tobytes()
    # formats OpenCV can't read (e.g. GIF); Pillow validated the upload already
    with Image.open(io.BytesIO(data)) as img:
        out = io.BytesIO()
        img.convert('RGB').save(out, 'JPEG', quality=90)
        return out.getvalue()


def task_id_for(version, owner, data):
    """
    Task ids are derived from the app version, the owner and the image, so
    uploading the same image twice returns the existing task. The digest is
    keyed with SECRET_KEY because the id is also part of the media URLs.
    """
    m = hmac.new(settings.SECRET_KEY.encode('utf-8'), digestmod='md5')
    m.update(version.encode('utf-8'))
    m.update((owner.email if not owner.is_anonymous else '').encode('utf-8'))
    m.update(data)
    return m.hexdigest()

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
        # File.Meta resolves to TimeStampedModel.Meta here, so repeat the ordering
        ordering = ('-modified', '-created',)


class ViewableQuerySet(models.query.QuerySet):

    def viewable_by(self, user):
        return self.filter(owner=user)


class SingleImageUploadManager(models.Manager):

    def create(self, file, owner, folder=None, **kwargs): # QuerySet, file=file, owner=user
        """
        Create a CellTaskModel from a validated UploadedFile object.
        folder=None is the user's Home folder (#98).
        """
        # app
        app_name = self.model.__module__.split('.')[0]
        app = sys.modules[app_name]

        # read to memory
        file.seek(0)
        uploaded_file_data = file.read()

        # Generate task id
        task_id = task_id_for(app.version, owner, uploaded_file_data)

        existing_queryset = self.filter(id=task_id)
        if existing_queryset.exists():
            logger.info('%s: task %s already exists', app_name, task_id)
            existing = existing_queryset[0]
            existing.is_existing = True
            return existing

        # get image format
        image_type = image_type_of(uploaded_file_data)
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

        # save uploaded image data to file
        # (FILE_UPLOAD_DIRECTORY_PERMISSIONS lets the worker write results)
        obj.uploaded_image.save(uploaded_image_path, ContentFile(uploaded_file_data), save=False)

        # convert to jpeg for web display
        display_data = display_jpeg(uploaded_file_data)
        obj.uploaded_display.save(uploaded_display_path, ContentFile(display_data), save=False)

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
    result = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)

    objects = SingleImageUploadManager.from_queryset(ViewableQuerySet)()

    class Meta(Task.Meta):
        abstract = True

# TODO: Permissions class for sharing
