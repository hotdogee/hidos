"""hidos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from datetime import datetime

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path

from allauth.account.views import ConfirmEmailView, password_reset_from_key
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from app import views as app_views
from app.forms import BootstrapAuthenticationForm
from users.serializers import GoogleLoginSerializer
from users.views import RegisterView


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    serializer_class = GoogleLoginSerializer  # checks the token's audience


urlpatterns = [
    re_path(r'^results/(?P<file_id>[0-9a-fA-F-]{32,36})$', app_views.task_result, name='task-result'),
    re_path(r'^login$',
        auth_views.LoginView.as_view(
            template_name='app/login.html',
            authentication_form=BootstrapAuthenticationForm,
            extra_context={
                'title': 'Log in',
                'year': datetime.now().year,
            },
        ),
        name='login'),
    re_path(r'^logout$',
        auth_views.LogoutView.as_view(next_page='/'),
        name='logout'),
    # the link in password reset emails sent by /api/v1/auth/password/reset/
    re_path(r'^accounts/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$', password_reset_from_key,
        name='password_reset_confirm'),
    path('accounts/', include('allauth.urls')),

    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),

    path('api/v1/cell/', include('cell.urls')),
    path('api/v1/fs/', include('fs.urls', namespace='fs')),
    re_path(r'^api/v1/auth/registration/$', RegisterView.as_view(), name='rest_register'),
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    re_path(r'^api/v1/auth/facebook/$', FacebookLogin.as_view(), name='facebook_login'),
    re_path(r'^api/v1/auth/google/$', GoogleLogin.as_view(), name='google_login'),
    re_path(r'^confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(),
        name='account_confirm_email'),  # TODO: implement this in client
]

# Serving files uploaded by a user during development
# (in production nginx serves MEDIA_ROOT, see docker/nginx.conf)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# EmailConfirmation table not used because we're using EmailConfirmationHMAC, hide its admin
from allauth.account.models import EmailConfirmation  # noqa: E402
if admin.site.is_registered(EmailConfirmation):
    admin.site.unregister(EmailConfirmation)
