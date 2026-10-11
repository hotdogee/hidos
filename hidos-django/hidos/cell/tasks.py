import sys
import json
import math
import time
import traceback
from os import path, stat

import urllib3

from celery import Task
from celery.utils.log import get_task_logger
from celery.signals import after_task_publish, task_success, task_failure

from django.conf import settings
from django.core.cache import cache
from django.db import DatabaseError, transaction
from django.utils import timezone


logger = get_task_logger(__name__)


def json_safe(value):
    """
    Analysis results contain NumPy scalars and arrays (and sometimes NaN);
    turn them into plain JSON values for the result JSONField.
    """
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if hasattr(value, 'tolist'):  # numpy arrays and scalars
        return json_safe(value.tolist())
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def report_error(app_name, task_record, error):
    """Post a failed task to Slack (#63) when SLACK_WEBHOOK_URL is set."""
    if not settings.SLACK_WEBHOOK_URL:
        return
    data = {
        'channel': settings.SLACK_CHANNEL, 'username': app_name,
        'icon_emoji': ':desktop_computer:',
        'text': '{0}\n{1}\n{2}\n`{3}`'.format(
            task_record.owner.email if task_record.owner else '-', task_record.name,
            error, path.basename(task_record.uploaded_image.name)
        ),
    }
    try:
        slack_manager = urllib3.PoolManager(1)
        slack_manager.request('POST', settings.SLACK_WEBHOOK_URL,
            body=json.dumps(data), headers={'Content-Type': 'application/json'}, timeout=10)
    except Exception:
        logger.exception('Could not send the error report to Slack')


def save_fields(task_record, fields):
    """
    Save only the fields the worker changes, so a rename or move made while
    the analysis runs is kept. Returns False if the task was deleted
    meanwhile (a full save would have inserted it again).
    """
    try:
        with transaction.atomic():  # savepoint, in case we run inside a transaction
            task_record.save(update_fields=fields + ['modified'])
        return True
    except DatabaseError:  # "Save with update_fields did not affect any rows."
        return False


class CellTask(Task):

    def process_image(self, app_name, task_id, logger=logger):
        app = sys.modules[app_name]
        model = app.models.Task
        func = app.run

        # update dequeue time, status and progress bar
        task_record = model.objects.filter(id__exact=task_id).first()
        if task_record is None:
            logger.info('{0} worker: task {1} was deleted before it started'.format(app_name, task_id))
            return task_id
        task_record.dequeued = timezone.now()
        task_record.status = 'running'
        task_record.progress = 0.1
        if not save_fields(task_record, ['dequeued', 'status', 'progress']):
            return task_id
        logger.info('{0} worker {1}: {2}'.format(app_name, task_record.status, task_id))

        # run
        try:
            task_record.result = json_safe(func(task_record))
        except Exception as e:
            # record the failure so the task doesn't stay 'running' forever (#12)
            task_record.status = 'failed'
            task_record.error = traceback.format_exc()
            task_record.progress = 1.0
            task_record.finished = timezone.now()
            if not save_fields(task_record, ['status', 'error', 'progress', 'finished']):
                logger.info('{0} worker: task {1} was deleted during the analysis'.format(app_name, task_id))
                return task_id
            logger.error('{0} worker failed: {1} ({2}: {3})'.format(app_name, task_id, type(e).__name__, e))
            report_error(app_name, task_record, e.args[0] if e.args else repr(e))
            raise

        # update result state
        task_record.status = 'failed'
        if not path.isfile(task_record.result_image.path):
            task_record.status = 'NO_OUT_JPG'
        elif stat(task_record.result_image.path)[6] == 0:
            task_record.status = 'OUT_JPG_EMPTY'
        else:
            task_record.status = 'success'
            # convert to jpeg for web display
            #Image.open(task_record.result_image.path).save(task_record.result_display.path)

        task_record.progress = 1.0
        task_record.finished = timezone.now()
        if not save_fields(task_record, ['result', 'status', 'progress', 'finished']):
            logger.info('{0} worker: task {1} was deleted during the analysis'.format(app_name, task_id))
            return task_id
        logger.info('{0} worker {1}: {2}'.format(app_name, task_record.status, task_id))

        return task_id # passed to 'result' argument of task_success_handler


if settings.USE_CACHE:
    LOCK_EXPIRE = 30
    LOCK_ID = 'task_list_cache_lock'
    CACHE_ID = 'task_list_cache'
    acquire_lock = lambda: cache.add(LOCK_ID, 'true', LOCK_EXPIRE)
    release_lock = lambda: cache.delete(LOCK_ID)

@after_task_publish.connect
def task_sent_handler(sender=None, headers=None, body=None, **kwds):
    if settings.USE_CACHE:
        task_id = (headers or {}).get('id')
        args = body[0] if body else None
        while not acquire_lock():
            time.sleep(0.1)
        try:
            tlist = cache.get(CACHE_ID, [])
            if args:
                bid = args[0] # cell task id
                tlist.append( (task_id,bid) )
                logger.info('[task_sent] task sent: %s. queue length: %s' % (bid, len(tlist)) )
                cache.set(CACHE_ID, tlist)
            else:
                logger.info('[task_sent] no args. rabbit task_id: %s' % (task_id) )
        finally:
            release_lock()

@task_success.connect
def task_success_handler(sender=None, result=None, **kwds):
    if settings.USE_CACHE:
        while not acquire_lock():
            time.sleep(0.1)
        try:
            task_id = result
            tlist = cache.get(CACHE_ID, [])
            if tlist and task_id:
                for tuple in tlist:
                    if task_id in tuple:
                        tlist.remove(tuple)
                        logger.info('[task_success] task removed from queue: %s' % (task_id) )
                        break
                logger.info('[task_success] task done: %s. queue length: %s' % (task_id, len(tlist)) )
                cache.set(CACHE_ID, tlist)
            else:
                logger.info('[task_success] no queue list or cell task id.')
        finally:
            release_lock()

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None,args=None, kwargs=None, traceback=None, einfo=None, **kwds):
    if settings.USE_CACHE:
        logger.info('[task_failure] task failed. rabbit task_id: %s' % (task_id) )
        task_success_handler(sender, task_id)
