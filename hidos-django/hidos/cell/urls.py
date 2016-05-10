from django.conf.urls import include, url

from . import views


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^c2/', include('cellc2.urls', namespace='c2')),
    url(r'^c1/', include('cellc1.urls', namespace='c1')),
]
