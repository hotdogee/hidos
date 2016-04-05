from django.conf.urls import url

from . import views
from . import app_name

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<task_id>[0-9a-zA-Z]+)/$', views.DetailView.as_view(), name='detail'),
    # {% url "cellc2:tasks" %}
    url(r'^api/v1/tasks$', views.TaskListCreateView.as_view(), name='tasks'),
    # {% url "cellc2:tasks" task.task_id %}
    url(r'^api/v1/tasks/(?P<task_id>[0-9a-zA-Z]+)$', views.TaskReadUpdateDeleteView.as_view(), name='tasks'),
]
