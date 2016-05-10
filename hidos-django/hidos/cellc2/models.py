from __future__ import unicode_literals
import hashlib
import imghdr
import stat as Perm
from os import path, makedirs, chmod

from PIL import Image

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from cell.models import CellTaskModel, ViewableQuerySet
from .tasks import run_cell_c2_task
from . import app_name, verbose_name, version


class SingleImageUploadManager(models.Manager):

    def create(self, file, user, **kwargs): # QuerySet, file=file, user=user
        """
        Create a CellTaskModel from a validated UploadedFile object
        """
        uploaded_file_data = file.read()

        # Generate task id
        m = hashlib.md5()
        m.update(version)
        m.update(user.username) # if anonymous, username is ''
        m.update(uploaded_file_data)
        task_id = m.hexdigest()

        existing_queryset = self.filter(task_id=task_id)
        if existing_queryset.exists():
            return existing_queryset[0]

        # get image format
        image_type = imghdr.what('', uploaded_file_data)

        # Generate args_list and path_prefix
        path_prefix = path.join(settings.MEDIA_ROOT, 'cellc2', 'task', task_id, task_id)
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
        if p.mode.split(';')[1:2] == '16':
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
            'version': version,
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

class CellC2Task(CellTaskModel):
    cell_ratio = models.FloatField(null=True, blank=True)

    objects = SingleImageUploadManager.from_queryset(ViewableQuerySet)()

    def get_absolute_url(self):
        return reverse('c2:detail', kwargs={'task_id': self.task_id}, current_app=app_name)

    class Meta(CellTaskModel.Meta):
        verbose_name = '{0} {1}'.format(verbose_name, 'Task')

    def enqueue(self):
        """Insert task into task queue
        """
        # Generate args_list and path_prefix
        path_prefix = path.join(settings.MEDIA_ROOT, 'cellc2', 'task', self.task_id, self.task_id)
        script_path = path.join(settings.PROJECT_ROOT, 'cellc2', 'bin', '1_6_obj_area_cal_cmd.R')
        # avoid exploits, don't any part of the user filename
        uploaded_image_path = path_prefix + '_uploaded.' + self.uploaded_filetype
        result_image_path = path_prefix + '_result.' + self.uploaded_filetype
        result_json_path = path_prefix + '_result.json'
        # jpg image for viewer
        input_image_viewer_path = path_prefix + '_in.jpg'
        output_image_viewer_path = path_prefix + '_out.jpg'
        # build command
        # args_list = [[settings.R_SCRIPT, script_path, uploaded_image_path, result_image_path, result_json_path]]
        print(uploaded_image_path, result_image_path,result_json_path)
        run_cell_c2_task.delay(self.task_id, uploaded_image_path, result_image_path, result_json_path, path_prefix)

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None)
    # def save(self, *args, **kwargs):
    #     if self.name == "Yoko Ono's blog":
    #         return # Yoko shall never have her own blog!
    #     else:
    #         super(CellC2Task, self).save(*args, **kwargs) # Call the "real" save() method.
