"""
Definition of views.
"""

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpRequest
from django.http import JsonResponse
from datetime import datetime
from .models import CellQAnalysis
from django.http.response import HttpResponse
from django.conf import settings
from os import path, makedirs, chmod
from uuid import uuid4
from .tasks import run_cellq_task
import stat as Perm
import json
import hashlib
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.core.urlresolvers import reverse
import logging
import imghdr
from PIL import Image

version = '0.1'

# Get an instance of a logger
logger = logging.getLogger(__name__)

def tasks(request):
    """returns task list for logged in user"""
    if not request.user.is_authenticated():
        return JsonResponse({})
    else:
        current_tz = timezone.get_current_timezone()
        return JsonResponse({
            'data': [{
                'id': t.task_id,
                'name': t.user_filename,
                'url': reverse('retrieve', kwargs={'task_id': t.task_id}),
                'result_img': settings.MEDIA_URL + 'cellq/task/' + t.task_id + '/' + t.task_id + '_out.jpg',
                'input_img': settings.MEDIA_URL + 'cellq/task/' + t.task_id + '/' + t.task_id + '_in.jpg',
                'result': json.loads(t.result or '{}'),
                'result_outerr': json.loads(t.result_outerr or '{}'),
                'result_status': t.result_status,
                'created': current_tz.normalize(t.enqueue_date.astimezone(current_tz)).isoformat(),
                } for t in CellQAnalysis.objects.filter(user=request.user)]
            })

def status(request):
    task_ids = []
    if request.method == 'GET':
        task_ids = request.GET.getlist('id')
    elif request.method == 'POST':
        task_ids = request.POST.getlist('id')
    else:
        return JsonResponse({})
    if not task_ids:
        return JsonResponse({})
    return JsonResponse({
        'data': [{
            'id': t.task_id,
            'name': t.user_filename,
            'result_outerr': json.loads(t.result_outerr or '{}'),
            'result_status': t.result_status,
            } for t in CellQAnalysis.objects.filter(task_id__in=task_ids)]
        })

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    if request.method == 'GET':
        return render(
            request,
            'cellq/index.html',
            {
                'title': 'Cell Q',
                'year': datetime.now().year,
                'version': version,
            }
        )
    elif request.method == 'POST':
        # error detection
        if 'file' not in request.FILES:
            return HttpResponse('Invalid file')
        uploaded_file = request.FILES['file']
        uploaded_file_data = uploaded_file.read()
        
        # check if file is image
        image_type = imghdr.what('', uploaded_file_data)
        if not image_type:
            logger.info('Uploaded image type is unsupported, filename: {0}'.format(uploaded_file.name))
            return HttpResponse('Uploaded image type is unsupported')
        else:
            logger.info('Uploaded image type: {0}, filename: {1}'.format(image_type, uploaded_file.name))
            
        # calculate file hash
        m = hashlib.md5()
        m.update(version)
        if request.user.is_authenticated():
            m.update(request.user.username)
        m.update(uploaded_file_data)
        task_id = m.hexdigest()
        # check database for duplicate
        if not CellQAnalysis.objects.filter(task_id=task_id).exists():
            logger.info('New task_id: {0}'.format(task_id))
            # setup file paths
            #task_id = uuid4().hex # TODO: Create from hash of input to check for duplicate inputs
            path_prefix = path.join(settings.MEDIA_ROOT, 'cellq', 'task', task_id, task_id)
            original_image_path = path_prefix + '_in.' + image_type # avoid exploits, don't any part of the user filename
            input_image_path = path_prefix + '_in.jpg'
            output_image_path = path_prefix + '_out.jpg'
            output_json_path = path_prefix + '_out.json'
            
            # create directory
            if not path.exists(path.dirname(path_prefix)):
                makedirs(path.dirname(path_prefix))
            chmod(path.dirname(path_prefix), Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO) # ensure the standalone dequeuing process can open files in the directory
        
            # write original image data to file
            with open(original_image_path, 'wb') as original_image_f:
                original_image_f.write(uploaded_file_data)
            chmod(original_image_path, Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO) # ensure the standalone dequeuing process can access the file
                  
            # convert to jpeg for web display
            Image.open(original_image_path).save(input_image_path)
            chmod(input_image_path, Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO) # ensure the standalone dequeuing process can access the file

            # build command
            # set R_Script="C:\Program Files\R\R-3.2.2\bin\RScript.exe"
            # "C:\Program Files\R\R-3.2.2\bin\RScript.exe" 1_1_CellQ_han.R "171-1 40x_c005_24.96.JPG" "171-1 40x_c005_24.96_out.JPG" "171-1 40x_c005_24.96.json"
            script_path = path.join(settings.PROJECT_ROOT, 'cellq', 'bin', 'r_cellq_sever_run.R')
            args_list = [[settings.R_SCRIPT, script_path, original_image_path, output_image_path, output_json_path]]
        
            # insert entry into database
            record = CellQAnalysis()
            record.task_id = task_id
            record.version = version
            record.user_filename = uploaded_file.name
            record.result_status = 'queued'
            if request.user.is_authenticated():
                record.user = request.user
            record.save()

            run_cellq_task.delay(task_id, args_list, path_prefix)
        else:
            logger.info('Duplicate task_id: {0}'.format(task_id))
            
        # debug
        #run_cellq_task.delay(task_id, args_list, path_prefix).get()
        return HttpResponse(task_id)

def retrieve(request, task_id='1'):
    #return HttpResponse("retrieve = %s." % (task_id))
    try:
        record = CellQAnalysis.objects.get(task_id=task_id)
        return render(
            request,
            'cellq/result.html',
            {
                'title': 'Cell Q - {0}'.format(record.user_filename),
                'year': datetime.now().year,
                'version': record.version,
                'user_filename': record.user_filename,
            }
        )
    except ObjectDoesNotExist:
        message = 'Result not found'
        return render(
            request,
            'cellq/error.html',
            {
                'title': 'Cell Q Error',
                'year': datetime.now().year,
                'version': version,
                'message': message,
            }
        )
    except Exception as e:
        message = 'Result not found ({0})'.format(e.message)
        return render(
            request,
            'cellq/error.html',
            {
                'title': 'Cell Q Error',
                'year': datetime.now().year,
                'version': version,
                'message': message,
            }
        )