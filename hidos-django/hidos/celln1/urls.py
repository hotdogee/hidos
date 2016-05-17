from django.conf.urls import url

from . import api
from . import views
from . import app_name # application namespace


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<task_id>[0-9a-zA-Z]+)$', views.DetailView2.as_view(), name='detail'),
    # {% url "cellc1:tasks" %}
    url(r'^api/v1/tasks$', api.TaskViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='task-list'),
    url(r'^api/v1/tasks/running$', api.TaskViewSet.as_view({
        'get': 'running',
    }), name='task-running'),
    # {% url "cellc1:tasks" task.task_id %}
    url(r'^api/v1/tasks/(?P<task_id>[0-9a-zA-Z]+)$', api.TaskViewSet.as_view({
        'get': 'retrieve',
        #'put': 'update',
        #'patch': 'partial_update',
        'delete': 'destroy'
    }), name='task-detail'),
]
