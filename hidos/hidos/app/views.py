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

version = '0.6.1'

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
    return render(request, 'app/homepage.html')