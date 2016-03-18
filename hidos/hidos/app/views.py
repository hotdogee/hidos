"""
Definition of views.
"""

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpRequest
from django.http import JsonResponse
from datetime import datetime
from .models import ImageAnalysis
from django.http.response import HttpResponse
from django.conf import settings
from os import path, makedirs, chmod
from uuid import uuid4
from .tasks import run_image_analysis_task
import stat as Perm
import json
import hashlib
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.core.urlresolvers import reverse

version = '0.8'

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
                'result_img': settings.MEDIA_URL + 'image_analysis/task/' + t.task_id + '/' + t.task_id + '_out.jpg',
                'input_img': settings.MEDIA_URL + 'image_analysis/task/' + t.task_id + '/' + t.task_id + '_in.jpg',
                'result': json.loads(t.result or '{}'),
                'result_status': t.result_status,
                'created': current_tz.normalize(t.enqueue_date.astimezone(current_tz)).isoformat(),
                } for t in ImageAnalysis.objects.filter(user=request.user)]
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
            'result_status': t.result_status,
            } for t in ImageAnalysis.objects.filter(task_id__in=task_ids)]
        })

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    if request.method == 'GET':
        return render(
            request,
            'app/index.html',
            {
                'title':'Home',
                'year':datetime.now().year,
                'version': version,
            }
        )
    elif request.method == 'POST':
        # error detection
        if 'file' not in request.FILES:
            return HttpResponse('Invalid file')
        uploaded_file = request.FILES['file']
        # calculate file hash
        m = hashlib.md5()
        m.update(version)
        if request.user.is_authenticated():
            m.update(request.user.username)
        for chunk in uploaded_file.chunks():
            m.update(chunk)
        task_id = m.hexdigest()
        # check database for duplicate
        if not ImageAnalysis.objects.filter(task_id=task_id).exists():
            # setup file paths
            #task_id = uuid4().hex # TODO: Create from hash of input to check for duplicate inputs
            path_prefix = path.join(settings.MEDIA_ROOT, 'image_analysis', 'task', task_id, task_id)
            input_image_path = path_prefix + '_in.jpg'
            output_image_path = path_prefix + '_out.jpg'
            output_json_path = path_prefix + '_out.json'

            if not path.exists(path.dirname(input_image_path)):
                makedirs(path.dirname(input_image_path))
            chmod(path.dirname(input_image_path), Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO) # ensure the standalone dequeuing process can open files in the directory
        
            # write query to file
            if 'file' in request.FILES:
                with open(input_image_path, 'wb') as input_image_f:
                    for chunk in uploaded_file.chunks():
                        input_image_f.write(chunk)
            chmod(input_image_path, Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO) # ensure the standalone dequeuing process can access the file

            # build command
            # set R_Script="C:\Program Files\R\R-3.2.2\bin\RScript.exe"
            # %R_Script% 1_6_obj_area_cal_cmd.R IMG_0159.JPG IMG_0159_out.JPG IMG_0159_out.csv
            script_path = path.join(settings.PROJECT_ROOT, 'app', 'bin', '1_6_obj_area_cal_cmd.R')
            args_list = [[settings.R_SCRIPT, script_path, input_image_path, output_image_path, output_json_path]]
        
            # insert entry into database
            record = ImageAnalysis()
            record.task_id = task_id
            record.version = version
            record.user_filename = uploaded_file.name
            record.result_status = 'queued'
            if request.user.is_authenticated():
                record.user = request.user
            record.save()

            run_image_analysis_task.delay(task_id, args_list, path_prefix)

        # debug
        #run_image_analysis_task.delay(task_id, args_list, path_prefix).get()
        return HttpResponse(task_id)

def retrieve(request, task_id='1'):
    #return HttpResponse("retrieve = %s." % (task_id))
    try:
        record = ImageAnalysis.objects.get(task_id=task_id)
        return render(
            request,
            'app/result.html',
            {
                'title': 'CellQ - {0}'.format(record.user_filename),
                'year': datetime.now().year,
                'version': record.version,
                'user_filename': record.user_filename,
            }
        )
    except ObjectDoesNotExist:
        message = 'Result not found'
        return render(
            request,
            'app/error.html',
            {
                'title': 'CellQ Error',
                'year': datetime.now().year,
                'version': version,
                'message': message,
            }
        )
    except Exception as e:
        message = 'Result not found ({0})'.format(e.message)
        return render(
            request,
            'app/error.html',
            {
                'title': 'CellQ Error',
                'year': datetime.now().year,
                'version': version,
                'message': message,
            }
        )