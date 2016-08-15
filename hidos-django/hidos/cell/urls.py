from django.conf.urls import include, url

#from . import views


urlpatterns = [
    #url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^a1/', include('cella1.urls', namespace='cella1')),
    url(r'^c1/', include('cellc1.urls', namespace='cellc1')),
    url(r'^c2/', include('cellc2.urls', namespace='cellc2')),
    url(r'^m1/', include('cellm1.urls', namespace='cellm1')),
    url(r'^m3/', include('cellm3.urls', namespace='cellm3')),
    url(r'^n1/', include('celln1.urls', namespace='celln1')),
]
