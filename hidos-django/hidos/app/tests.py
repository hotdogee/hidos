"""
Tests for the web pages served by Django itself (login, result viewer,
admin, health check).
"""
import json
import os
import re
import subprocess
import sys

import pytest
from allauth.account.models import EmailAddress
from django.contrib import admin
from django.urls import reverse

from conftest import LOOKALIKE, PASSWORD, VICTIM, make_user
from hidos.settings.base import PROJECT_ROOT, REPO_ROOT
from fs.tests import create_folder, create_task, fake_run

pytestmark = pytest.mark.django_db


@pytest.fixture
def fake_cellc2(monkeypatch):
    import cellc2
    monkeypatch.setattr(cellc2, 'run', fake_run({'confluence': '42.00'}))


def test_healthz(client):
    response = client.get('/healthz')
    assert response.status_code == 200 and response.json() == {'status': 'ok'}


def test_login_page_logs_in_and_redirects(client, user):
    page = client.get('/login?next=/results/abc')
    assert page.status_code == 200
    html = page.content.decode()
    assert 'action="/login"' in html
    assert reverse('account_signup') in html and reverse('account_reset_password') in html
    response = client.post('/login', {'username': user.email, 'password': PASSWORD, 'next': '/admin/'})
    assert response.status_code == 302 and response['Location'] == '/admin/'
    assert '_auth_user_id' in client.session


def test_login_page_refuses_unconfirmed_email(client, api_client):
    """Like the login API: signing up with someone else's address must not give a session."""
    make_user('unv@example.com', verified=False)
    response = client.post('/login', {'username': 'unv@example.com', 'password': PASSWORD, 'next': '/admin/'})
    assert response.status_code == 200
    assert '_auth_user_id' not in client.session
    assert 'has not been confirmed yet' in response.content.decode()
    assert client.get('/accounts/3rdparty/').status_code == 302  # to the login page


def test_login_refuses_unconfirmed_email_with_a_confirmed_lookalike(client, api_client):
    """Confirming victim@gmaıl.com doesn't confirm victim@gmail.com, whatever PostgreSQL's iexact says."""
    user = make_user(VICTIM, verified=False)  # e.g. a Facebook login with someone else's address
    EmailAddress.objects.create(user=user, email=LOOKALIKE, verified=True)  # then added under /accounts/email/
    response = client.post('/login', {'username': VICTIM, 'password': PASSWORD})
    assert response.status_code == 200 and '_auth_user_id' not in client.session
    response = api_client.post('/api/v1/auth/login/', {'email': VICTIM, 'password': PASSWORD}, format='json')
    assert response.status_code == 400


def test_login_page_wrong_password(client, user):
    response = client.post('/login', {'username': user.email, 'password': 'nope'})
    assert response.status_code == 200
    assert 'Please enter a correct email and password.' in response.content.decode()


def test_logout_is_post_only(client, user):
    client.force_login(user)
    assert client.get('/logout').status_code == 405
    assert client.post('/logout').status_code == 302
    assert '_auth_user_id' not in client.session


def test_account_menu_shows_the_user_and_posts_logout(client, user):
    """#49: the menu showed the (non-existent) username and opened over its button."""
    client.force_login(user)
    html = client.get('/login').content.decode()
    assert '>Alice<i class="material-icons right">arrow_drop_down' in html
    assert 'action="/logout" method="post"' in html
    assert 'belowOrigin: true, alignment: "right"' in html

def test_allauth_pages_are_under_accounts(client):
    assert reverse('account_login') == '/accounts/login/'
    assert client.get('/accounts/signup/').status_code == 200


def test_confirm_email_link_points_to_confirm_view():
    assert reverse('account_confirm_email', args=['abc']) == '/confirm-email/abc/'


# --- result viewer (#66) ------------------------------------------------------------

def test_result_page_shows_images_fit_to_frame(client, user, auth_client, fake_cellc2):
    data = create_task(auth_client)
    client.force_login(user)
    response = client.get('/results/' + data['id'])
    assert response.status_code == 200
    html = response.content.decode()
    # both images start at "fit the whole image" magnification
    assert html.count('class="viewer fit z-depth-1" data-zoom="fit"') == 2
    assert '_uploaded_display.jpg' in html and '_result_display.jpg' in html
    assert 'confluence' in html and '42.00' in html


def test_result_page_while_running_refreshes(client, user, auth_client, fake_cellc2):
    from cellc2.models import Task
    data = create_task(auth_client)
    Task.objects.filter(pk=data['id']).update(status='running')
    client.force_login(user)
    html = client.get('/results/' + data['id']).content.decode()
    assert 'http-equiv="refresh"' in html and '_result_display.jpg' not in html


def test_result_page_is_private(client, other_user, auth_client, fake_cellc2):
    data = create_task(auth_client)
    assert client.get('/results/' + data['id']).status_code == 302  # login required
    client.force_login(other_user)
    assert client.get('/results/' + data['id']).status_code == 404


def test_result_page_for_folder_is_404(client, user, auth_client):
    folder = create_folder(auth_client, 'A')
    client.force_login(user)
    assert client.get('/results/' + folder['id']).status_code == 404


def test_task_absolute_url_is_the_result_page(auth_client, fake_cellc2):
    from cellc2.models import Task
    task = Task.objects.get(pk=create_task(auth_client)['id'])
    assert task.get_absolute_url() == '/results/' + task.id.hex


# --- Google Analytics (#13, #14) ---------------------------------------------------------

def test_google_analytics_off_by_default(client):
    assert 'googletagmanager' not in client.get('/login').content.decode()


def test_google_analytics_when_configured(client, settings):
    settings.GOOGLE_ANALYTICS_ID = 'G-TEST123'
    html = client.get('/login').content.decode()
    assert 'googletagmanager.com/gtag/js?id=G-TEST123' in html
    assert "page_title: 'Log in'" in html


def test_google_analytics_does_not_get_task_ids_or_names(client, user, auth_client, settings, fake_cellc2):
    """Task ids are in the public media URLs, so the result page must not report them (#13)."""
    settings.GOOGLE_ANALYTICS_ID = 'G-TEST123'
    data = create_task(auth_client)
    client.force_login(user)
    html = client.get('/results/' + data['id']).content.decode()
    gtag = html[html.index("gtag('config'"):]
    gtag = gtag[:gtag.index('</script>')]
    assert "page_title: 'Result'" in gtag
    assert data['id'] not in gtag and data['name'] not in gtag
    assert r"location.pathname.replace(/^\/results\/.*/, '/results/')" in gtag
    assert 'location.href' not in gtag and 'location.search' not in gtag


# --- admin ------------------------------------------------------------------------------

def test_admin_pages_load(client, auth_client, fake_cellc2):
    from django.contrib.auth import get_user_model
    folder = create_folder(auth_client, 'A')
    create_task(auth_client, folder['id'])
    superuser = get_user_model().objects.create_superuser('root@example.com', PASSWORD)
    client.force_login(superuser)
    for model, model_admin in admin.site._registry.items():
        info = (model._meta.app_label, model._meta.model_name)
        changelist = client.get(reverse('admin:%s_%s_changelist' % info), {'q': 'a'})
        assert changelist.status_code == 200, info
        obj = model._default_manager.first()
        if obj is not None:
            change = client.get(reverse('admin:%s_%s_change' % info, args=[obj.pk]))
            assert change.status_code == 200, info
        add = client.get(reverse('admin:%s_%s_add' % info))
        assert add.status_code in (200, 403), info


def test_healthz_ignores_host_and_https_settings(client, settings):
    """The container health check calls http://127.0.0.1:8000/healthz."""
    settings.ALLOWED_HOSTS = ['cell.example.org']
    settings.SECURE_SSL_REDIRECT = True
    assert client.get('/healthz', HTTP_HOST='127.0.0.1:8000').status_code == 200
    assert client.get('/login', HTTP_HOST='127.0.0.1:8000').status_code == 400


def test_throttling_uses_the_proxy_address(settings, rf):
    """With NUM_PROXIES a client can't get fresh rate limits by sending X-Forwarded-For."""
    from rest_framework.settings import api_settings
    from rest_framework.throttling import AnonRateThrottle
    settings.REST_FRAMEWORK = {**settings.REST_FRAMEWORK, 'NUM_PROXIES': 1}
    api_settings.reload()
    try:
        idents = {AnonRateThrottle().get_ident(rf.get('/', HTTP_X_FORWARDED_FOR='%s, 10.0.0.9' % fake, REMOTE_ADDR='172.18.0.5'))
                  for fake in ('1.1.1.1', '2.2.2.2')}
        assert idents == {'10.0.0.9'}
    finally:
        api_settings.reload()


# --- deployed defaults (#96, #26) ----------------------------------------------------------
# The test settings set API_SESSION_AUTH and NUM_PROXIES themselves; these
# check what a deployment gets.

DEPLOYED_SETTINGS = """
import json
import environ
environ.Env.read_env = classmethod(lambda cls, *args, **kwargs: None)  # the code defaults, not a local .env
from django.conf import settings
print(json.dumps(list(settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'])))
"""


def deployed_settings(module, secret_key='k' * 20 + 'abcdefghijklmnopqrstuvwxyz0123456789'):
    env = {k: v for k, v in os.environ.items() if k not in ('API_SESSION_AUTH', 'NUM_PROXIES')}
    env.update(DJANGO_SETTINGS_MODULE=module, DJANGO_SECRET_KEY=secret_key)
    return subprocess.run([sys.executable, '-c', DEPLOYED_SETTINGS], cwd=PROJECT_ROOT, env=env,
                          capture_output=True, text=True)


@pytest.mark.parametrize('module', ['hidos.settings.production', 'hidos.settings.staging'])
def test_deployed_api_does_not_accept_sessions(module):
    result = deployed_settings(module)
    assert result.returncode == 0, result.stderr
    classes = json.loads(result.stdout)
    assert 'rest_framework_simplejwt.authentication.JWTAuthentication' in classes
    assert not any('Session' in c for c in classes)


@pytest.mark.parametrize('key', ['change-me', 'x' * 60, 'django-insecure-' + 'abcdefghij' * 5])
def test_production_refuses_placeholder_secret_keys(key):
    result = deployed_settings('hidos.settings.production', secret_key=key)
    assert result.returncode != 0 and 'DJANGO_SECRET_KEY' in result.stderr


def test_env_example_leaves_the_secret_key_empty():
    """Copying .env.example must not give a working key, so compose's ${DJANGO_SECRET_KEY:?} check fires."""
    with open(os.path.join(REPO_ROOT, '.env.example'), encoding='utf-8') as fh:
        assert re.search(r'^DJANGO_SECRET_KEY=$', fh.read(), re.M)


def test_compose_sets_num_proxies_for_nginx():
    """Without NUM_PROXIES the rate limits trust the client's X-Forwarded-For."""
    with open(os.path.join(REPO_ROOT, 'docker-compose.yml'), encoding='utf-8') as fh:
        compose = fh.read()
    assert re.search(r'^    NUM_PROXIES: \$\{NUM_PROXIES:-1\}$', compose, re.M)
    with open(os.path.join(REPO_ROOT, 'docker', 'nginx.conf'), encoding='utf-8') as fh:
        assert 'X-Forwarded-For $proxy_add_x_forwarded_for' in fh.read()
