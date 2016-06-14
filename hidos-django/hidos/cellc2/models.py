from __future__ import absolute_import, unicode_literals
from os import path

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from cell.models import File, CellTask, ViewableQuerySet, SingleImageUploadManager
from .tasks import run_cell_c2_task
from . import app_name, verbose_name, version

class CellC2Task(CellTask):
    cell_ratio = models.FloatField(null=True, blank=True)
    count_min = models.FloatField(null=True, blank=True)
    count_max = models.FloatField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('c2:detail', kwargs={'id': self.id}, current_app=app_name)

    class Meta(CellTask.Meta):
        verbose_name = '{0} {1}'.format(verbose_name, 'Task')

    def enqueue(self):
        """Insert task into task queue
        """
        # Generate args_list and path_prefix
        path_prefix = path.join(settings.MEDIA_ROOT, 'cellc2', 'task', self.id, self.id)
        script_path = path.join(settings.PROJECT_ROOT, 'cellc2', 'bin', '1_6_obj_area_cal_cmd.R')
        # avoid exploits, don't any part of the user filename
        uploaded_image_path = path_prefix + '_uploaded.' + self.uploaded_filetype
        result_image_path = path_prefix + '_result.' + self.uploaded_filetype
        result_json_path = path_prefix + '_result.json'
        # jpg image for viewer
        input_image_viewer_path = path_prefix + '_in.jpg'
        output_image_viewer_path = path_prefix + '_out.jpg'
        # build command
        args_list = [[settings.R_SCRIPT, script_path, uploaded_image_path, result_image_path, result_json_path]]
        run_cell_c2_task.delay(self.id, args_list, path_prefix)

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None)
    # def save(self, *args, **kwargs):
    #     if self.name == "Yoko Ono's blog":
    #         return # Yoko shall never have her own blog!
    #     else:
    #         super(CellC2Task, self).save(*args, **kwargs) # Call the "real" save() method.
