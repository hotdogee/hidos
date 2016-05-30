from __future__ import absolute_import, unicode_literals
import json
import time
from pytz import utc
from os import path, stat
from itertools import groupby
from subprocess import Popen, PIPE
from datetime import datetime, timedelta

from PIL import Image

from celery import shared_task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from celery.signals import task_sent, task_success, task_failure

from django.conf import settings
from django.core.cache import cache
import urllib3

from cellc2.bin.cellConfluence_singleTask import cellConfluence_singleTask
logger = get_task_logger(__name__)

if settings.USE_CACHE:
    LOCK_EXPIRE = 30
    LOCK_ID = 'task_list_cache_lock'
    CACHE_ID = 'task_list_cache'
    acquire_lock = lambda: cache.add(LOCK_ID, 'true', LOCK_EXPIRE)
    release_lock = lambda: cache.delete(LOCK_ID)

@shared_task(bind=True) # ignore_result=True
def run_cell_c2_task(self, task_id, uploaded_image_path, result_image_path, result_json_path, path_prefix):
    import django
    django.setup()

    self.app.log.redirect_stdouts_to_logger(logger)
    logger.info('image_analysis task_id: %s' % (task_id,))

    # update dequeue time
    from .models import CellC2Task
    record = CellC2Task.objects.get(task_id__exact=task_id)
    record.dequeued = datetime.utcnow().replace(tzinfo=utc)
    record.status = 'running'
    record.save()

    # slack report template
    slack_manager = urllib3.PoolManager(1)
    data = {"channel": "#image-bug", "username": "cellcloud", \
            "text": "",
            "icon_emoji": ":desktop_computer:"}



    # run
    try:
       cellConfluence_singleTask(uploaded_image_path, result_image_path, result_json_path)
    except Exception as e:
        record.stderr = e
        data["text"] = '`' + uploaded_image_path + '`\n' + e.args[0]
        slack_manager.request('POST','https://hooks.slack.com/services/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',body = json.dumps(data),headers={'Content-Type': 'application/json'})
        logger.info(e.args)

    # update result state
    record.status = 'failed'
    if not path.isfile(result_image_path):
        record.status = 'NO_OUT_JPG'
    elif stat(result_image_path)[6] == 0:
        record.status = 'OUT_JPG_EMPTY'
    elif not path.isfile(result_json_path):
        record.status = 'NO_OUT_JSON'
    elif stat(result_json_path)[6] == 0:
        record.status = 'OUT_JSON_EMPTY'
    else:
        record.status = 'success'
        with open(result_json_path, 'r') as f:
            result = json.load(f)
            record.cell_ratio = result['ratio']
        output_image_viewer_path = path_prefix + '_out.jpg'
        # convert to jpeg for web display
        Image.open(result_image_path).save(output_image_viewer_path)

    record.finished = datetime.utcnow().replace(tzinfo=utc)
    record.save()

    return task_id # passed to 'result' argument of task_success_handler

@task_sent.connect
def task_sent_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    if settings.USE_CACHE:
        while not acquire_lock():
            time.sleep(0.1)
        try:
            tlist = cache.get(CACHE_ID, [])
            if args:
                bid = args[0] # blast_task_id
                tlist.append( (task_id,bid) )
                #logger.info('[task_sent] task sent: %s. queue length: %s' % (bid, len(tlist)) )
                print('[task_sent] task sent: %s. queue length: %s' % (bid, len(tlist)) )
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
                logger.info('[task_success] no queue list or blast task id.')
        finally:
            release_lock()

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None,args=None, kwargs=None, traceback=None, einfo=None, **kwds):
    if settings.USE_CACHE:
        logger.info('[task_failure] task failed. rabbit task_id: %s' % (task_id) )
        task_success_handler(sender, task_id)
