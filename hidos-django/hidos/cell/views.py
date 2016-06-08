from datetime import datetime

from django.shortcuts import render

from vanilla import TemplateView, FormView

from . import app_name, verbose_name, version
from app.forms import BootstrapAuthenticationForm
from allauth.account.forms import SignupForm

class IndexView(TemplateView):
    template_name = 'cell/index_material.html'

    def get_context_data(self, **context):
        context['title'] = verbose_name
        context['year'] = datetime.now().year
        context['version'] = version
        return context

class RegisterView(FormView):
    template_name = 'app/register.html'
    form_class = SignupForm

    def get_form_class(self):
        return SignupForm




