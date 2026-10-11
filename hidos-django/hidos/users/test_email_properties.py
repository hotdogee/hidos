"""
Email addresses at every entry point that takes one (#67).

No address is a server error, and an address is stored and mailed as typed
or refused (users.adapter.AccountAdapter.clean_email).
"""
import re

import pytest
from allauth.account.models import EmailConfirmationHMAC
from allauth.account.utils import url_str_to_user_pk
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.test import Client
from rest_framework.test import APIClient

from conftest import PASSWORD, make_user
from users.emails import has_ascii_local_part

pytestmark = pytest.mark.django_db
User = get_user_model()

LOGIN = '/api/v1/auth/login/'
REGISTER = '/api/v1/auth/registration/'
RESEND = '/api/v1/auth/registration/resend-email/'
RESETS = ['/api/v1/auth/password/reset/', '/accounts/password/reset/']

# by code point, so that no editor normalizes them away
DOTLESS_I, DOTTED_CAPITAL_I, FULLWIDTH_AT = chr(0x0131), chr(0x0130), chr(0xFF20)


def stored(email):
    """How a typed address is stored: stripped and str.lower()-ed (allauth, UserManager)."""
    return email.strip().lower()


def account(email, verified=True):
    """An account with the address, also one that signup now refuses (made before, or by an operator)."""
    return make_user(stored(email), verified=verified)


def api():
    client = APIClient()
    client.raise_request_exception = False  # a crash is a 500 response, not an exception
    return client


def web():
    return Client(raise_request_exception=False)


def ok(response):
    assert response.status_code < 500, (response.status_code, response.content[:300])
    return response


CONFIRM_KEY = re.compile(r'/confirm-email/([-:\w]+)/')
RESET_UID = re.compile(r'/accounts/password/reset/key/([0-9a-z]+)-')


def tokens():
    """(recipients, user id, kind) of every confirmation and password reset link mailed."""
    found = []
    for message in mail.outbox:
        for key in CONFIRM_KEY.findall(message.body):
            confirmation = EmailConfirmationHMAC.from_key(key)
            if confirmation:
                found.append((tuple(message.to), confirmation.email_address.user_id, 'confirm'))
        for uid in RESET_UID.findall(message.body):
            found.append((tuple(message.to), int(url_str_to_user_pk(uid)), 'reset'))
    return found


def tokens_for(user):
    return [token for token in tokens() if token[1] == user.pk]


def signup(via, email):
    data = {'email': email, 'password1': PASSWORD, 'password2': PASSWORD}
    if via == 'rest':
        return ok(api().post(REGISTER, data, format='json'))
    return ok(web().post('/accounts/signup/', data))


# --- addresses that can't be stored or mailed as typed ----------------------------------------------

# Django's EmailValidator accepts İ ı ſ K before the @ (users.emails). A short run of them is mailed
# to no mailbox; Django 5.2's sanitize_address() raises ValueError on a longer one.
SHORT_NON_ASCII_LOCAL = 'v' + DOTLESS_I + 'ctim@gmail.com'
LONG_NON_ASCII_LOCAL = 'v' + DOTLESS_I * 24 + '@gmail.com'
LONG_DOTTED_I_LOCAL = DOTTED_CAPITAL_I * 20 + '@example.com'  # .lower(): 20 x (i + U+0307)
# Django's validator allows 320 characters, User.email and EmailAddress.email hold 254
OVERLONG = 'a' * 64 + '@' + ('b' * 63 + '.') * 3 + 'com'  # 260 characters
_domain = DOTTED_CAPITAL_I + 'x.' + 'b' * 63 + '.' + 'c' * 63 + '.com'
GROWS_PAST_254 = 'a' * (254 - 1 - len(_domain)) + '@' + _domain  # 254 characters, 255 lower-cased
CUT_ONTO = 'a' * 64 + '@' + 'b' * 63 + '.' + 'b' * 63 + '.' + 'b' * 61  # 254 characters
assert len(OVERLONG) == 260 and len(GROWS_PAST_254) == 254 and len(GROWS_PAST_254.lower()) == 255
assert len(CUT_ONTO) == 254


def _with_account(email):
    """An unconfirmed account with the address, if it could have been stored before it was refused."""
    try:
        validate_email(stored(email))
    except ValidationError:
        return
    if len(stored(email)) <= 254:
        account(email, verified=False)


def _rest_register(email):
    return [signup('rest', email)]


def _allauth_signup(email):
    return [signup('allauth', email)]


def _logins(email):
    _with_account(email)
    return [api().post(LOGIN, {'email': email, 'password': PASSWORD}, format='json'),
            web().post('/login', {'username': email, 'password': PASSWORD}),
            web().post('/accounts/login/', {'login': email, 'password': PASSWORD})]  # mails a confirmation


def _resets_without_account(email):
    return [web().post(url, {'email': email}) for url in RESETS]  # allauth mails "no account"


def _resets_with_account(email):
    _with_account(email)
    return [web().post(url, {'email': email}) for url in RESETS]


def _resend(email):
    _with_account(email)
    return [api().post(RESEND, {'email': email}, format='json')]


def _add_address(email):
    browser = web()
    browser.force_login(account('mallory@example.com'))
    return [browser.post('/accounts/email/', {'action_add': '', 'email': email})]


ENTRY_POINTS = {
    'rest-register': _rest_register,
    'allauth-signup': _allauth_signup,
    'logins': _logins,
    'resets-unknown-address': _resets_without_account,
    'resets-known-address': _resets_with_account,
    'resend-confirmation': _resend,
    'add-address': _add_address,
}


@pytest.mark.parametrize('entry', ENTRY_POINTS)
@pytest.mark.parametrize('email', [
    pytest.param(SHORT_NON_ASCII_LOCAL, id='short-non-ascii-local'),
    pytest.param(LONG_NON_ASCII_LOCAL, id='long-non-ascii-local'),
    pytest.param(LONG_DOTTED_I_LOCAL, id='long-dotted-i-local'),
    pytest.param(OVERLONG, id='overlong-260'),
    pytest.param(GROWS_PAST_254, id='254-grows-to-255'),
    pytest.param('victim@gmail.com.', id='trailing-dot'),  # invalid ones, refused everywhere
    pytest.param('victim' + FULLWIDTH_AT + 'gmail.com', id='fullwidth-at'),
    pytest.param('victim@gmail.com' + chr(0), id='nul'),
])
def test_odd_addresses_are_not_a_server_error_and_never_mailed(entry, email):
    for response in ENTRY_POINTS[entry](email):
        ok(response)
    assert [message.to for message in mail.outbox if not all(map(has_ascii_local_part, message.to))] == []


@pytest.mark.parametrize('via', ['rest', 'allauth'])
@pytest.mark.parametrize('typed', [
    pytest.param(OVERLONG, id='overlong-260'),
    pytest.param(GROWS_PAST_254, id='254-grows-to-255'),  # cut back to 254: .com became .co
    pytest.param(CUT_ONTO + 'x', id='255'),
])
def test_signup_registers_and_mails_the_typed_address_or_none(via, typed):
    """allauth cuts what it stores to fit User.email: a longer address was registered, and mailed, as another one."""
    signup(via, typed)
    assert set(User.objects.values_list('email', flat=True)) <= {stored(typed)}
    assert {address for message in mail.outbox for address in message.to} <= {stored(typed)}


@pytest.mark.parametrize('via', ['rest', 'allauth'])
def test_signup_with_an_address_cut_onto_an_existing_one(via):
    """That was an IntegrityError (HTTP 500)."""
    owner = account(CUT_ONTO)
    mail.outbox.clear()
    signup(via, CUT_ONTO + 'x')
    assert list(User.objects.values_list('pk', flat=True)) == [owner.pk]
    assert tokens_for(owner) == []
