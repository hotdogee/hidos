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


def test_logout_is_post_only(client, user):
    client.force_login(user)
    assert client.get('/logout').status_code == 405
    assert client.post('/logout').status_code == 302
    assert '_auth_user_id' not in client.session


def test_allauth_pages_are_under_accounts(client):
    assert reverse('account_login') == '/accounts/login/'
    assert client.get('/accounts/signup/').status_code == 200


def test_confirm_email_link_points_to_confirm_view():
    assert reverse('account_confirm_email', args=['abc']) == '/confirm-email/abc/'


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
