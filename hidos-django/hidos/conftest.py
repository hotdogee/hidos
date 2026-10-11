import io

import pytest
from PIL import Image
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

PASSWORD = 'correct-horse-battery-staple'

# Look-alike addresses (#67). PostgreSQL's UPPER(), which Django's iexact uses,
# maps the dotless i U+0131 to an ASCII "I", so iexact takes LOOKALIKE, a mailbox
# at another domain (xn--gmal-nza.com), for VICTIM. Python's str.lower() maps the
# Kelvin sign U+212A to an ASCII "k". On SQLite, whose LIKE only folds ASCII,
# the tests about iexact pass either way; CI runs them on PostgreSQL.
VICTIM = 'victim@gmail.com'
LOOKALIKE = 'victim@gma\u0131l.com'
KELVIN = '\u212aate@example.com'  # .lower() is kate@example.com


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path / 'media')
    settings.CHUNKED_UPLOAD_ROOT = str(tmp_path / 'chunked')
    return settings.MEDIA_ROOT


@pytest.fixture(autouse=True)
def clear_cache():
    # throttle counters live in the cache
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


def make_user(email, verified=True, **extra):
    from allauth.account.models import EmailAddress
    from django.contrib.auth import get_user_model
    user = get_user_model().objects.create_user(email=email, password=PASSWORD, **extra)
    EmailAddress.objects.create(user=user, email=email, primary=True, verified=verified)
    return user


@pytest.fixture
def user(db):
    return make_user('alice@example.com', first_name='Alice')


@pytest.fixture
def other_user(db):
    return make_user('bob@example.com')


@pytest.fixture
def api_client():
    return APIClient()


def jwt_client(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='JWT ' + str(RefreshToken.for_user(user).access_token))
    return client


@pytest.fixture
def auth_client(user):
    return jwt_client(user)


@pytest.fixture
def other_client(other_user):
    return jwt_client(other_user)


def image_file(name='cells.png', size=(64, 48), color=(120, 30, 200), fmt='PNG'):
    buf = io.BytesIO()
    Image.new('RGB', size, color).save(buf, fmt)
    buf.seek(0)
    buf.name = name
    return buf


@pytest.fixture
def png():
    return image_file()
