"""featGUI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^config/$', views.write_fsf, name='fconfig'),
    url(r'^running/$', views.new_job),
    url(r'^results/$', views.show_result, name='fresults'),
    url(r'^results/reg/$', views.show_reg, name='freg'),
    url(r'^results/prestats/$', views.show_prestats, name='fprestats'),
    url(r'^results/stats/$', views.show_stats, name='fstats'),
    url(r'^results/poststats/$', views.show_poststats, name='fpoststats'),
    url(r'^results/log/$', views.show_log, name='flog'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
