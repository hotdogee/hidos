from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.upload, name='icsi'),
    url(r'^api/v1/tasks$', views.tasks, name='tasks'),
    url(r'^api/v1/tasks/status$', views.status, name='status'),
    url(r'^(?P<task_id>[0-9a-zA-Z]+)$', views.retrieve, name='retrieve'),

]
