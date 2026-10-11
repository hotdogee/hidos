"""
Tests for the web pages served by Django itself (login, result viewer,
admin, health check).
"""
import pytest
from django.contrib import admin
from django.urls import reverse

from conftest import PASSWORD
from fs.tests import create_folder, create_task, fake_run

pytestmark = pytest.mark.django_db


@pytest.fixture
def fake_cellc2(monkeypatch):
    import cellc2
    monkeypatch.setattr(cellc2, 'run', fake_run({'confluence': '42.00'}))


def test_login_page_logs_in_and_redirects(client, user):
    page = client.get('/login?next=/results/abc')
    assert page.status_code == 200
    html = page.content.decode()
    assert 'action="/login"' in html
    assert reverse('account_signup') in html and reverse('account_reset_password') in html
    response = client.post('/login', {'username': user.email, 'password': PASSWORD, 'next': '/admin/'})
    assert response.status_code == 302 and response['Location'] == '/admin/'
    assert '_auth_user_id' in client.session


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
