from datetime import datetime

from django.shortcuts import render
from django.http import Http404

from vanilla import TemplateView
from vanilla import GenericModelView

from . import app_name, verbose_name, version
from .models import CellC2Task

logger = logging.getLogger(__name__) # __name__ == app.views


class IndexView(TemplateView):
    template_name = 'cellbase/index.html'

    def get_context_data(self, **context):
        context['title'] = verbose_name
        context['year'] = datetime.now().year
        context['version'] = version
        return context


class DetailView(GenericModelView):
    template_name = 'cellbase/result.html'
    model = CellC2Task
    lookup_field = 'task_id'

    def get_context_data(self, **context):
        context['title'] = '{0} - {1}'.format(verbose_name, self.object.user_filename)
        context['year'] = datetime.now().year
        context['version'] = version
        context['user_filename'] = self.object.user_filename
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