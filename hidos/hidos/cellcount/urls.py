from django.conf.urls import url
from .views import upload, tasks, status, retrieve  

urlpatterns = [
    url(r'^$', upload, name='cellcount'),
    url(r'^api/v1/tasks$', tasks, name='tasks'),
    url(r'^api/v1/tasks/status$', status, name='status'),
    url(r'^(?P<task_id>[0-9a-zA-Z]+)$', retrieve, name='retrieve'),

]
