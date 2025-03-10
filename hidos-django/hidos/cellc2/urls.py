﻿from django.conf.urls import url

from . import api
#from . import views
from . import app_name # application namespace


urlpatterns = [
    #url(r'^$', views.IndexView.as_view(), name='index'),
    #url(r'^(?P<id>[0-9a-zA-Z]+)$', views.DetailView.as_view(), name='detail'),
    # {% url "cellc2:tasks" %}
    url(r'^tasks$', api.TaskViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='task-list'),
    url(r'^tasks/running$', api.TaskViewSet.as_view({
        'get': 'running',
    }), name='task-running'),
    # {% url "cellc2:tasks" task.id %}
    url(r'^tasks/(?P<id>[0-9a-zA-Z]+)$', api.TaskViewSet.as_view({
        'get': 'retrieve',
        #'put': 'update',
        #'patch': 'partial_update',
        'delete': 'destroy'
    }), name='task-detail'),
]
