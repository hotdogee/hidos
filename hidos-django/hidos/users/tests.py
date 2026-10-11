import re
from unittest import mock

import jwt
import pytest
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialApp
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core import mail

from conftest import PASSWORD, image_file, make_user

pytestmark = pytest.mark.django_db
User = get_user_model()

LOGIN = '/api/v1/auth/login/'
REGISTER = '/api/v1/auth/registration/'
PROFILE = '/api/v1/auth/user/'


# --- local signup (#18) ---------------------------------------------------------

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


def test_password_reset_round_trip(api_client, client, user):
    """The reset email links to a working page (the URL name used to be missing: HTTP 500)."""
    response = api_client.post('/api/v1/auth/password/reset/', {'email': user.email}, format='json')
    assert response.status_code == 200, response.content
    link = re.search(r'https?://[^/\s]+(/accounts/password/reset/key/\S+)', mail.outbox[0].body).group(1)
    page = client.get(link, follow=True)
    assert page.status_code == 200
    new_password = 'another-long-passphrase-42'
    done = client.post(page.redirect_chain[-1][0] if page.redirect_chain else link,
                       {'password1': new_password, 'password2': new_password})
    assert done.status_code == 302
    login = api_client.post(LOGIN, {'email': user.email, 'password': new_password}, format='json')
    assert login.status_code == 200


# --- profile (#74, #75, #76) --------------------------------------------------------

def test_profile_get_and_update(auth_client, user):
    data = auth_client.get(PROFILE).json()
    assert data['email'] == user.email
    assert data['organization'] == '' and data['language'] == 'en' and data['image'] is None
    response = auth_client.patch(PROFILE, {'organization': 'Meridigen', 'language': 'zh-hant',
                                           'email': 'hijack@example.com', 'is_staff': True}, format='json')
    assert response.status_code == 200, response.content
    user.refresh_from_db()
    assert user.organization == 'Meridigen' and user.language == 'zh-hant'
    assert user.email == 'alice@example.com' and not user.is_staff  # read only


def test_profile_language_must_be_supported(auth_client):
    assert auth_client.patch(PROFILE, {'language': 'klingon'}, format='json').status_code == 400


def test_profile_image_upload(auth_client, user, settings):
    response = auth_client.patch(PROFILE, {'image': image_file('me.png')}, format='multipart')
    assert response.status_code == 200, response.content
    user.refresh_from_db()
    assert user.image.name.startswith('users/images/') and 'me' not in user.image.name
    settings.PROFILE_IMAGE_MAX_BYTES = 10
    assert auth_client.patch(PROFILE, {'image': image_file('big.png')}, format='multipart').status_code == 400


def test_profile_requires_authentication(api_client):
    assert api_client.get(PROFILE).status_code == 401


# --- social accounts are merged by email (#67) ---------------------------------------

@pytest.fixture
def google_app():
    app = SocialApp.objects.create(provider='google', name='Google', client_id='id', secret='secret')
    app.sites.add(Site.objects.get_current())
    return app


def google_login(api_client, email, email_verified=True, uid='google-uid-1', audience='id'):
    from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter

    def complete_login(self, request, app, token, response=None, **kwargs):
        provider = self.get_provider()
        return provider.sociallogin_from_response(request, {
            'id': uid, 'sub': uid, 'email': email, 'email_verified': email_verified,
            'verified_email': email_verified, 'name': 'Google User', 'given_name': 'Google', 'family_name': 'User'})

    tokeninfo = mock.Mock(status_code=200, json=lambda: {'aud': audience, 'azp': audience, 'email': email})
    with mock.patch.object(GoogleOAuth2Adapter, 'complete_login', complete_login),             mock.patch('users.serializers.requests.get', return_value=tokeninfo) as get:
        response = api_client.post('/api/v1/auth/google/', {'access_token': 'fake-token'}, format='json')
    assert get.call_args.kwargs['params'] == {'access_token': 'fake-token'}
    return response


def test_social_login_merges_with_local_account(api_client, user, google_app):
    response = google_login(api_client, user.email)
    assert response.status_code == 200, response.content
    assert response.json()['user']['email'] == user.email
    assert User.objects.count() == 1
    account = SocialAccount.objects.get(provider='google')
    assert account.user == user
    user.refresh_from_db()
    assert user.has_usable_password()  # local login keeps working


def test_social_login_creates_account_for_new_email(api_client, google_app):
    response = google_login(api_client, 'carol@example.com', uid='google-uid-2')
    assert response.status_code == 200, response.content
    user = User.objects.get(email='carol@example.com')
    assert SocialAccount.objects.get(provider='google').user == user
    # then a local signup with the same email is refused instead of creating a duplicate
    assert api_client.post(REGISTER, {'email': 'carol@example.com', 'password1': PASSWORD,
                                      'password2': PASSWORD}, format='json').status_code == 400


@pytest.fixture
def facebook_app():
    app = SocialApp.objects.create(provider='facebook', name='Facebook', client_id='fb-id', secret='secret')
    app.sites.add(Site.objects.get_current())
    return app


def facebook_login(api_client, email, uid='fb-uid-1'):
    from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter

    def complete_login(self, request, app, token, **kwargs):
        return self.get_provider().sociallogin_from_response(request, {
            'id': uid, 'email': email, 'name': 'Facebook User', 'first_name': 'Facebook', 'last_name': 'User'})

    with mock.patch.object(FacebookOAuth2Adapter, 'complete_login', complete_login):
        return api_client.post('/api/v1/auth/facebook/', {'access_token': 'fake-fb-token'}, format='json')


def test_social_login_is_not_merged_into_unverified_local_account(api_client, google_app):
    """Someone who signed up with another person's (unconfirmed) email must not get their Google login."""
    squatter = make_user('dave@example.com', verified=False)
    # e.g. connected under /accounts/3rdparty/ before the owner of the address shows up
    SocialAccount.objects.create(user=squatter, provider='facebook', uid='fb-squatter')
    response = google_login(api_client, 'dave@example.com', uid='google-uid-3')
    assert response.status_code == 400
    assert 'access' not in response.json()
    assert not SocialAccount.objects.filter(provider='google').exists()


def test_google_login_is_not_merged_into_facebook_account_with_the_same_email(api_client, google_app, facebook_app):
    """Facebook emails are unverified: a Facebook signup can't capture the address's later Google logins."""
    response = facebook_login(api_client, 'victim@example.com', uid='fb-attacker')
    assert response.status_code == 200, response.content
    attacker = User.objects.get(email='victim@example.com')
    response = google_login(api_client, 'victim@example.com', uid='google-victim')
    assert response.status_code == 400
    assert not SocialAccount.objects.filter(provider='google').exists()
    assert set(SocialAccount.objects.filter(user=attacker).values_list('provider', flat=True)) == {'facebook'}


def test_google_login_is_not_merged_into_account_with_the_email_as_unconfirmed_second_address(
        client, api_client, google_app):
    attacker = make_user('mallory@example.com')
    client.force_login(attacker)
    response = client.post('/accounts/email/', {'action_add': '', 'email': 'victim@example.com'})
    assert response.status_code in (200, 302)
    assert EmailAddress.objects.filter(user=attacker, email='victim@example.com', verified=False).exists()
    response = google_login(api_client, 'victim@example.com', uid='google-victim')
    assert response.status_code == 200, response.content
    assert response.json()['user']['email'] == 'victim@example.com'  # a new account, not mallory's
    assert not SocialAccount.objects.filter(user=attacker).exists()


def test_google_token_issued_to_another_app_is_rejected(api_client, user, google_app):
    """A token from another site's Google sign-in must not log into the matching local account."""
    response = google_login(api_client, user.email, audience='someone-elses-client-id')
    assert response.status_code == 400
    assert 'access' not in response.json()
    assert not SocialAccount.objects.exists()


def test_unverified_social_email_is_not_merged(api_client, user, google_app):
    response = google_login(api_client, user.email, email_verified=False, uid='google-uid-4')
    assert not SocialAccount.objects.filter(user=user).exists()
    assert User.objects.filter(email=user.email).count() == 1
    assert response.status_code == 400


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
