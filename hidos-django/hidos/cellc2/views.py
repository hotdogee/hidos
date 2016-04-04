from datetime import datetime

from django.shortcuts import render

from vanilla import TemplateView

from . import app_name, verbose_name

class IndexView(TemplateView):
    template_name = 'cellbase/index.html'
    def get_context_data(self, **context):
        context['title'] = verbose_name
        context['year'] = datetime.now().year
        context['version'] = version
        return context
