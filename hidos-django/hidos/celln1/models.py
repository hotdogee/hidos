from __future__ import unicode_literals
import hashlib
import imghdr
import stat as Perm
from os import path, makedirs, chmod

from PIL import Image

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from cell.models import CellTaskModel, ViewableQuerySet, SingleImageUploadManager
from .tasks import run_cell_n1_task
from . import app_name, verbose_name, version
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


from django.utils.html import format_html

class CellN1Task(CellTaskModel):
    cell_body = models.IntegerField(null=True, blank=True)
    outgrowth_length = models.IntegerField(null=True, blank=True)
    mean_length = models.FloatField(null=True, blank=True)
    number_of_branches = models.IntegerField(null=True, blank=True)
    mean_branch = models.FloatField(null=True, blank=True)
    neurite_outgrowth = models.IntegerField(null=True, blank=True)
    mean_outgrowth = models.FloatField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('n1:detail', kwargs={'task_id': self.task_id}, current_app=app_name)

    class Meta(CellTaskModel.Meta):
        verbose_name = '{0} {1}'.format(verbose_name, 'Task')

    def enqueue(self):
        """Insert task into task queue
        """
        # Generate args_list and path_prefix
        path_prefix = path.join(settings.MEDIA_ROOT, 'celln1', 'task', self.task_id, self.task_id)
        # avoid exploits, don't any part of the user filename
        uploaded_image_path = path_prefix + '_uploaded.' + self.uploaded_filetype
        result_image_path = path_prefix + '_result.' + self.uploaded_filetype
        result_json_path = path_prefix + '_result.json'
        # jpg image for viewer
        input_image_viewer_path = path_prefix + '_in.jpg'
        output_image_viewer_path = path_prefix + '_out.jpg'
        # build command
        run_cell_n1_task.delay(self.task_id, input_image_viewer_path, result_image_path, result_json_path, path_prefix)
        print(uploaded_image_path, input_image_viewer_path, result_json_path)

    def original_image(self):
        return format_html('<a href="/media/celln1/task/{}/{}_in.jpg">Uploaded Image</a>', self.task_id,
                           self.task_id)

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None)
    # def save(self, *args, **kwargs):
    #     if self.name == "Yoko Ono's blog":
    #         return # Yoko shall never have her own blog!
    #     else:
    #         super(CellC2Task, self).save(*args, **kwargs) # Call the "real" save() method.
