"""
Definition of views.
"""
import logging
import uuid
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from cell.models import CellTask
from fs.models import File

logger = logging.getLogger(__name__)


@login_required
def task_result(request, file_id):
    """
    Result viewer for an analysis task. Both images open scaled to fit the
    page (#66); clicking an image switches between fit and 100%.
    """
    try:
        file = File.objects.select_related('content_type').get(pk=uuid.UUID(file_id), owner=request.user)
    except (ValueError, File.DoesNotExist):
        raise Http404('Result not found')
    task = file.content
    if not isinstance(task, CellTask):
        raise Http404('Result not found')
    result = task.result if isinstance(task.result, dict) else {'result': task.result}
    return render(request, 'app/result.html', {
        'title': '{0} - {1}'.format(task._meta.app_config.verbose_name, task.name),
        'year': datetime.now().year,
        'task': task,
        'app_name': task._meta.app_config.verbose_name,
        'result_items': sorted(result.items()),
        'finished': task.status not in ('queued', 'running'),
    })
