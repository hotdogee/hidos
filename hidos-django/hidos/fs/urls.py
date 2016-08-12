from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import api
from . import views
from . import app_name # application namespace

# url(r'^api/v1/fs/', include('fs.urls', namespace='fs')),

urlpatterns = [
    # # {% url "fs:folders" %}
    # url(r'^folders$', api.FolderViewSet.as_view({
    #     'get': 'list', # list user root files, maybe redundent?
    #     'post': 'create',
    # }), name='folder-list'),
    # # {% url "fs:folders" folder.id %}
    # url(r'^folders/(?P<pk>[0-9a-zA-Z]+)$', api.FolderViewSet.as_view({
    #     'get': 'retrieve', # includes content list
    #     'put': 'update',
    #     'patch': 'partial_update',
    #     'delete': 'destroy'
    # }), name='folder-detail'),
    # {% url "fs:files" %}
    url(r'^$', api.FileViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='file-list'),
    # {% url "fs:files" file.id %}
    url(r'^/(?P<pk>[0-9a-zA-Z]+)$', api.FileViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='file-detail'),
    # user friendly folder path urls are to be implemented in client code
]
