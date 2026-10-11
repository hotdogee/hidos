"""
Remove a task's images from MEDIA_ROOT when the task is deleted, directly or
through its folder (#23). Before this the files stayed on disk and remained
reachable by URL after the user deleted the task.
"""
import logging
import shutil
from os import path

from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import CellTask

logger = logging.getLogger(__name__)


@receiver(post_delete)
def delete_task_files(sender, instance, **kwargs):
    if not isinstance(instance, CellTask) or not instance.uploaded_image:
        return
    task_dir = path.dirname(path.join(settings.MEDIA_ROOT, instance.uploaded_image.name))
    media_root = path.abspath(settings.MEDIA_ROOT)
    if path.abspath(task_dir).startswith(media_root + path.sep) and path.isdir(task_dir):
        shutil.rmtree(task_dir, ignore_errors=True)
        logger.info('deleted files of task %s', instance.id.hex)
