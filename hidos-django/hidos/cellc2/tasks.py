from __future__ import absolute_import, unicode_literals
import json
import time
import urllib3
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

from .bin import process_image as process_image_bin

logger = get_task_logger(__name__)

@shared_task() # ignore_result=True
def process_image(task_id):
    import django
    django.setup()

    logger.info('image_analysis task_id: %s' % (task_id,))

    # update dequeue time
    from .models import Task
    task_record = Task.objects.get(id__exact=task_id)
    task_record.dequeued = datetime.utcnow().replace(tzinfo=utc)
    task_record.status = 'running'
    task_record.progress = 0.1
    task_record.save()

    # run
    try:
        task_record.result = process_image_bin(task_record)
    except Exception as e:
        task_record.stderr = e
        # slack report templatera
        import urllib3
        slack_manager = urllib3.PoolManager(1)
        data = {"channel": "#image-bug", "username": "cellc2",
                "text": "",
                "icon_emoji": ":desktop_computer:"}
        data["text"] = task_record.owner.username + '\n' + task_record.name + '\n' + e.args[0]  + '\n' + '`' + task_record.uploaded_image.path.split('/')[-1] + '`'
        slack_manager.request('POST','https://hooks.slack.com/services/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',body = json.dumps(data),headers={'Content-Type': 'application/json'})
        logger.info(e.args)
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
    task_record.finished = datetime.utcnow().replace(tzinfo=utc)
    task_record.save()

    return task_id # passed to 'result' argument of task_success_handler


if settings.USE_CACHE:
    LOCK_EXPIRE = 30
    LOCK_ID = 'task_list_cache_lock'
    CACHE_ID = 'task_list_cache'
    acquire_lock = lambda: cache.add(LOCK_ID, 'true', LOCK_EXPIRE)
    release_lock = lambda: cache.delete(LOCK_ID)

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
