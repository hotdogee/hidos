from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpRequest
from django.http import JsonResponse
from datetime import datetime
from .models import ICSIImageAnalysis, OvumGrade
from django.http.response import HttpResponse
from django.conf import settings
from uuid import uuid4
from .tasks import run_image_analysis_task
import stat as Perm
import json
import hashlib
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.core.urlresolvers import reverse
from os import chmod, mkdir, path

version = '0.1.0'

# Create your views here.

def ovums(request):
    """returns task list for logged in user"""
    if not request.user.is_authenticated():
        return JsonResponse({})
    else:
        current_tz = timezone.get_current_timezone()
        
        ICSIImageAnalysis_get_by_user = ICSIImageAnalysis.objects.filter(user=request.user)
        ovum_objects = []
        for analysis in ICSIImageAnalysis_get_by_user:
            for ovum in analysis.ovums.all():
                ovum_objects.append(ovum)
        
    
        return JsonResponse({
            'data': [{
                'count': t.ovum_number,
                'name': t.parent_imageanalysis.user_filename,
                #'url': reverse('icsi_retrieve', kwargs={'task_id': t.task_id}),
                'url': 'test',
                'result_img': settings.MEDIA_URL + 'icsi/task/' + t.parent_imageanalysis.task_id + '/' + t.parent_imageanalysis.task_id + '_Crop' + str(t.ovum_number) + '.jpg',
                'input_img': settings.MEDIA_URL + 'icsi/task/' + t.parent_imageanalysis.task_id + '/' + t.parent_imageanalysis.task_id + '_in.jpg',
                'grade': t.grade,
                'result_status': t.status,
                'created': current_tz.normalize(t.graded_time.astimezone(current_tz)).isoformat(),
                } for t in ovum_objects]
            }) 



def tasks(request):
    if not request.user.is_authenticated():
        return JsonResponse({})
    else:
        current_tz = timezone.get_current_timezone()
        
        tmp = JsonResponse({
            'data': [{
                'id': t.task_id,
                'name': t.user_filename,
                'input_img': settings.MEDIA_URL + 'icsi/task/' + t.task_id + '/' + t.task_id + '_in.jpg',
                'status': t.result_status,
                'created': current_tz.normalize(t.enqueue_date.astimezone(current_tz)).isoformat(),
                } for t in ICSIImageAnalysis.objects.filter(user=request.user)]
            })

        print(tmp)

        return tmp


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
            'created': current_tz.normalize(t.enqueue_date.astimezone(current_tz)).isoformat(),
            } for t in ICSIImageAnalysis.objects.filter(task_id__in=task_ids)]
        })




def retrieve(request, task_id='1'):
    #return HttpResponse("retrieve = %s." % (task_id))
    try:
        record = ICSIImageAnalysis.objects.get(task_id=task_id)
        return render(
            request,
            'icsi/result.html',
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


def upload(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    if request.method == 'GET':
        return render(
            request,
            'icsi/index.html',
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
        if not ICSIImageAnalysis.objects.filter(task_id=task_id).exists():
            # setup file paths
            #task_id = uuid4().hex # TODO: Create from hash of input to check for duplicate inputs
            path_prefix = path.join(settings.MEDIA_ROOT, 'icsi', 'task', task_id, task_id)
            input_image_path = path_prefix + '_in.jpg'
            output_image_path = path_prefix
            # output_json_path = path_prefix + '_out.json'

            if not path.exists(path.dirname(input_image_path)):
                mkdir(path.dirname(input_image_path))
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
            script_path = path.join(settings.PROJECT_ROOT, 'icsi', 'bin', 'crop_auto.py')
            args_list = [[settings.PYTHON_SCRIPT, script_path,'--input', input_image_path,'--output',output_image_path]]
        
            # insert entry into database
            record = ICSIImageAnalysis()
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
        return HttpResponse('icsi')

