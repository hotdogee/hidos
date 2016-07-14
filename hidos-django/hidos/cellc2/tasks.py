from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger

from cell.tasks import CellTask

from . import app_name

logger = get_task_logger(__name__)

@shared_task(base=CellTask) # ignore_result=True
def analysis(task_id):
    return analysis.process_image(app_name, task_id, logger)
    