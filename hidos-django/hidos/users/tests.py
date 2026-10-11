import re

import jwt
import pytest
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core import mail

from conftest import PASSWORD

pytestmark = pytest.mark.django_db
User = get_user_model()

LOGIN = '/api/v1/auth/login/'
REGISTER = '/api/v1/auth/registration/'


# --- registration ----------------------------------------------------------------

def test_register_sends_confirmation_and_requires_it(api_client):
    response = api_client.post(REGISTER, {
        'email': 'new@example.com', 'password1': PASSWORD, 'password2': PASSWORD,
        'first_name': 'New', 'last_name': 'User'}, format='json')
    assert response.status_code == 201, response.content
    user = User.objects.get(email='new@example.com')
    assert user.first_name == 'New' and user.has_usable_password()
    assert len(mail.outbox) == 1
    link = re.search(r'https?://\S+/confirm-email/(\S+)/', mail.outbox[0].body)
    assert link, mail.outbox[0].body
    # not verified yet
    assert api_client.post(LOGIN, {'email': user.email, 'password': PASSWORD}, format='json').status_code == 400
    # confirm the address like the link in the email does
    confirm = api_client.post('/confirm-email/%s/' % link.group(1))
    assert confirm.status_code in (200, 302)
    assert EmailAddress.objects.get(email='new@example.com').verified
    assert api_client.post(LOGIN, {'email': user.email, 'password': PASSWORD}, format='json').status_code == 200


def test_register_rejects_existing_email_case_insensitively(api_client, user):
    response = api_client.post(REGISTER, {
        'email': 'ALICE@example.com', 'password1': PASSWORD, 'password2': PASSWORD}, format='json')
    assert response.status_code == 400
    assert 'email' in response.json()


def test_register_validates_passwords(api_client):
    assert api_client.post(REGISTER, {'email': 'x@example.com', 'password1': PASSWORD,
                                      'password2': PASSWORD + 'x'}, format='json').status_code == 400
    assert api_client.post(REGISTER, {'email': 'x@example.com', 'password1': '123',
                                      'password2': '123'}, format='json').status_code == 400


def test_confirmation_email_uses_site_domain(api_client):
    api_client.post(REGISTER, {'email': 'n@example.com', 'password1': PASSWORD, 'password2': PASSWORD}, format='json')
    assert settings.SITE_DOMAIN in mail.outbox[0].body


# --- login / JWT ------------------------------------------------------------

def test_login_returns_jwt(api_client, user):
    response = api_client.post(LOGIN, {'email': user.email, 'password': PASSWORD}, format='json')
    assert response.status_code == 200, response.content
    data = response.json()
    assert data['token'] == data['access']  # `token` kept for the djangorestframework-jwt era client
    assert data['refresh']
    assert data['user']['email'] == user.email
    payload = jwt.decode(data['access'], options={'verify_signature': False})
    assert payload['email'] == user.email
    assert payload['full_name'] == 'Alice'
    assert 'username' not in payload  # #95


def test_refresh_token(api_client, user):
    refresh = api_client.post(LOGIN, {'email': user.email, 'password': PASSWORD}, format='json').json()['refresh']
    response = api_client.post('/api/v1/auth/token/refresh/', {'refresh': refresh}, format='json')
    assert response.status_code == 200 and response.json()['access']


def test_login_wrong_password(api_client, user):
    assert api_client.post(LOGIN, {'email': user.email, 'password': 'wrong'}, format='json').status_code == 400


def test_inactive_user_cannot_login(api_client, user):
    user.is_active = False
    user.save()
    assert api_client.post(LOGIN, {'email': user.email, 'password': PASSWORD}, format='json').status_code == 400


# --- sites (#78) -------------------------------------------------------------------

def test_site_domain_migration():
    site = Site.objects.get(pk=settings.SITE_ID)
    assert site.domain == settings.SITE_DOMAIN == 'hidos.io'
    assert site.name == settings.SITE_NAME


# --- admin --------------------------------------------------------------------------

def test_create_superuser_with_email_only():
    admin = User.objects.create_superuser('root@example.com', PASSWORD)
    assert admin.is_staff and admin.is_superuser
    assert str(admin) == 'root@example.com'
    assert admin.get_short_name() == 'root'
