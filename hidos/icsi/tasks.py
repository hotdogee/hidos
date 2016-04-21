"""
if you edit the tasks.py (in any app),
you must restart the celery server to refresh the code.
(gan, takes me so much to figure it out..)

"""




from __future__ import absolute_import
from celery import shared_task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from subprocess import Popen, PIPE
from datetime import datetime, timedelta
from .models import Task, Ovum
from os import path, stat
from pytz import utc
from itertools import groupby
from celery.utils.log import get_task_logger
from celery.signals import task_sent, task_success, task_failure
from django.core.cache import cache
from django.conf import settings
import json
import time
import glob

logger = get_task_logger(__name__)


if settings.USE_CACHE:
    LOCK_EXPIRE = 30
    LOCK_ID = 'task_list_cache_lock'
    CACHE_ID = 'task_list_cache'
    acquire_lock = lambda: cache.add(LOCK_ID, 'true', LOCK_EXPIRE)
    release_lock = lambda: cache.delete(LOCK_ID)

@shared_task() # ignore_result=True
def run_image_analysis_task(task_id, args_list, path_prefix):
    import django
    django.setup()
    logger.info("icsi_analysis task_id: %s" % (task_id,))

    # update dequeue time
    record = Task.objects.get(task_id__exact=task_id)
    record.dequeue_date = datetime.utcnow().replace(tzinfo=utc)
    record.result_status = 'running'
    record.save()

    # run
    for args in args_list:
        logger.info(args)
	Popen(args, stdin=PIPE, stdout=PIPE).wait()

    # update result state
    result_status = ''
    with open('/'.join(path_prefix.split('/')[:-1]) + '/predict_result.json') as data_file:
        predict_result = json.load(data_file)


    crop_img_path = glob.glob(path_prefix+'_Crop[1-9].jpg')
    record.result_status = 'failed'
    if len(crop_img_path) == 0:
       result_status = 'NO_OUT_JPG'
       logger.info("There is no output.")
    else:
        record.number_of_ovum = len(crop_img_path)
        record.result_status = 'success'
        ovum_count = 1

        # sum up ML result
        ovum_A = 0
        ovum_B = 0
        ovum_C = 0
        ovum_D = 0
        ovum_E = 0

        for crop in crop_img_path:
            file_name = crop.split('/')[-1]
            predict_score = float(predict_result[file_name])
            logger.info(predict_score) 
            ovum = Ovum()
            if predict_score < 0.5:
                ovum.grade = "A"
                ovum_A +=1
            else:
                ovum.grade = "E"
                ovum_E +=1


            logger.info("cropping")
            ovum.ovum_id = task_id + '_Crop' + str(ovum_count)
            ovum.ovum_number = ovum_count
            ovum_count += 1
            ovum.parent_imageanalysis = Task(task_id = task_id)
            ovum.status = 'success'
            ovum.archived = False



            ovum.graded_time = datetime.utcnow().replace(tzinfo=utc)
            ovum.save()

        record.number_of_A = ovum_A
        record.number_of_B = ovum_B
        record.number_of_C = ovum_C
        record.number_of_D = ovum_D
        record.number_of_E = ovum_E
        record.result_date = datetime.utcnow().replace(tzinfo=utc)
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
