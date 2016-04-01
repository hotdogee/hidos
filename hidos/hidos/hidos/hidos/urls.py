"""
Definition of urls for hidos.
"""

from datetime import datetime
from django.conf.urls import include, url
from app.forms import BootstrapAuthenticationForm
from django.contrib.auth import views as auth_views
from app import views as app_views

# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r'^$', app_views.home, name='home'),
    url(r'^api/v1/tasks$', app_views.tasks, name='tasks'),
    url(r'^api/v1/tasks/status$', app_views.status, name='status'),
    url(r'^login/$',
        auth_views.login,
        {
            'template_name': 'app/login.html',
            'authentication_form': BootstrapAuthenticationForm,
            'extra_context':
            {
                'title': 'Log in',
                'year': datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        auth_views.logout,
        {
            'next_page': '/',
        },
        name='logout'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^(?P<task_id>[0-9a-zA-Z]+)$', app_views.retrieve, name='retrieve'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]

# Serving files uploaded by a user during development
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
