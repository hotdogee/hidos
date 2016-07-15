from datetime import datetime
import logging

from django.shortcuts import render
from django.http import Http404, HttpResponse

from vanilla import TemplateView
from vanilla import GenericModelView

from . import app_name, verbose_name, version
from .models import CellN1Task

logger = logging.getLogger(__name__) # __name__ == cellc1.views


class IndexView(TemplateView):
    template_name = 'celln1/index.html'

    def get_context_data(self, **context):
        context['title'] = verbose_name
        context['year'] = datetime.now().year
        context['version'] = version
        return context


class DetailView2(GenericModelView):
    template_name = 'celln1/result.html'
    model = CellN1Task
    lookup_field = 'task_id'

    def get_context_data(self, **context):
        context['title'] = '{0} - {1}'.format(verbose_name, self.object.uploaded_filename)
        context['year'] = datetime.now().year
        context['version'] = version
        context['user_filename'] = self.object.uploaded_filename
        if self.object.feedback_satisfied:
            context['feedbacked'] = True
        else:
            context['feedbacked'] = False

        return context

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            context = self.get_context_data()
            return self.render_to_response(context)
        except Http404:
            self.template_name = 'app/error.html'
            message = 'Result not found'
            return self.render_to_response({
                'title': '{0} - {1}'.format(verbose_name, 'Error'),
                'year': datetime.now().year,
                'version': version,
                'message': message,
            })
        except Exception as e:
            self.template_name = 'app/error.html'
            message = 'Result not found ({0})'.format(e.message)
            return self.render_to_response({
                'title': '{0} - {1}'.format(verbose_name, 'Error'),
                'year': datetime.now().year,
                'version': version,
                'message': message,
            })


def feedback(request, task_id):
    try:
        task = CellN1Task.objects.get(task_id = task_id)
        task.feedback_satisfied = request.POST.get('answer')
        task.save()
        return HttpResponse('success')
    except Http404:
        return HttpResponse('error')


def feedback_opinions(request, task_id):
    try:
        task = CellN1Task.objects.get(task_id = task_id)
        task.feedback_opinions = request.POST.get('opinions')
        task.save()
        return HttpResponse('success')
    except Http404:
        return HttpResponse('error')
