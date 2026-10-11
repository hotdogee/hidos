import os

import numpy as np
import pytest

from conftest import image_file
from fs.models import File
from fs.tests import create_folder, create_task, fake_run

pytestmark = pytest.mark.django_db

TASKS = '/api/v1/cell/c2/tasks'


@pytest.fixture
def fake_cellc2(monkeypatch):
    import cellc2
    monkeypatch.setattr(cellc2, 'run', fake_run({'confluence': np.float64(12.5), 'count': np.int64(3)}))


def get_task(task_id):
    from cellc2.models import Task
    return Task.objects.get(pk=task_id)


def test_create_task_in_home_folder(auth_client, user, fake_cellc2):
    """Tasks can be created in Home, i.e. without a folder (#98)."""
    data = create_task(auth_client)
    assert data['folder'] is None
    assert data['type'] == 'cellc2'
    assert data['name'] == 'cells.png'
    task = get_task(data['id'])
    # CELERY_TASK_ALWAYS_EAGER: the (fake) analysis already ran
    assert task.status == 'success'
    assert task.result == {'confluence': 12.5, 'count': 3}
    assert task.owner == user
    assert task.dequeued and task.finished
    home = auth_client.get('/api/v1/fs/home').json()
    assert data['id'] in [f['id'] for f in home['files']]


def test_create_task_in_folder(auth_client, fake_cellc2):
    folder = create_folder(auth_client, 'Plate')
    data = create_task(auth_client, folder['id'])
    assert data['folder'] == folder['id']
    listed = auth_client.get('/api/v1/fs/' + folder['id']).json()['files']
    assert [f['id'] for f in listed] == [data['id']]


def test_uploaded_file_name_is_not_used_on_disk(auth_client, fake_cellc2):
    task = get_task(create_task(auth_client, image=image_file('../../evil.png'))['id'])
    assert task.name == 'evil.png'
    assert '..' not in task.uploaded_image.name
    assert task.uploaded_image.name.endswith('_uploaded.png')


def test_failed_analysis_is_recorded(auth_client, monkeypatch):
    """A crashing algorithm marks the task failed instead of leaving it 'running' (#12)."""
    import cellc2

    def broken(task_record):
        raise ValueError('cannot analyze this image')
    monkeypatch.setattr(cellc2, 'run', broken)
    task = get_task(create_task(auth_client)['id'])
    assert task.status == 'failed'
    assert 'cannot analyze this image' in task.error
    assert task.finished is not None


def test_failed_task_is_reported_to_slack_only_when_configured(auth_client, monkeypatch, settings):
    import cellc2
    import urllib3
    calls = []

    class Pool:
        def __init__(self, *a, **k):
            pass

        def request(self, method, url, **kwargs):
            calls.append((method, url, kwargs['body']))

    monkeypatch.setattr(urllib3, 'PoolManager', Pool)
    monkeypatch.setattr(cellc2, 'run', lambda record: 1 / 0)
    create_task(auth_client, image=image_file(color=(1, 1, 1)))
    assert calls == []
    settings.SLACK_WEBHOOK_URL = 'https://hooks.slack.invalid/T000/B000/XXX'
    create_task(auth_client, image=image_file(color=(2, 2, 2)))
    assert len(calls) == 1 and calls[0][1] == settings.SLACK_WEBHOOK_URL
    assert 'alice@example.com' in calls[0][2]


def test_missing_result_image_status(auth_client, monkeypatch):
    import cellc2
    monkeypatch.setattr(cellc2, 'run', lambda record: {'ratio': 1})
    assert get_task(create_task(auth_client)['id']).status == 'NO_OUT_JPG'


def test_same_image_from_two_users_gives_two_tasks(auth_client, other_client, fake_cellc2):
    a = create_task(auth_client)
    b = create_task(other_client)
    assert a['id'] != b['id']


def test_task_ids_depend_on_secret_key(settings, user):
    from cell.models import task_id_for
    a = task_id_for('0.8', user, b'image')
    settings.SECRET_KEY = 'another-secret-key-for-this-test-only-123456'
    assert task_id_for('0.8', user, b'image') != a
    assert len(a) == 32


def test_invalid_upload_is_rejected(auth_client):
    bad = image_file()
    bad = type(bad)(b'not an image')
    bad.name = 'x.png'
    assert auth_client.post(TASKS, {'file': bad}, format='multipart').status_code == 400
    assert auth_client.post(TASKS, {}, format='multipart').status_code == 400
    assert not File.objects.exists()


def test_upload_size_limit(auth_client, settings):
    settings.TASK_UPLOAD_MAX_BYTES = 10
    assert auth_client.post(TASKS, {'file': image_file()}, format='multipart').status_code == 400


def test_cannot_use_someone_elses_folder(auth_client, other_client, fake_cellc2):
    folder = create_folder(auth_client, 'Mine')
    response = other_client.post(TASKS, {'file': image_file(), 'folder': folder['id']}, format='multipart')
    assert response.status_code == 400


def test_anonymous_cannot_submit(api_client):
    assert api_client.post(TASKS, {'file': image_file()}, format='multipart').status_code == 401


def test_task_submission_is_rate_limited(auth_client, settings, fake_cellc2):
    """#26"""
    settings.REST_FRAMEWORK = {**settings.REST_FRAMEWORK, 'DEFAULT_THROTTLE_RATES': {
        **settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'], 'task_submit': '2/min'}}
    from rest_framework.settings import api_settings
    from rest_framework.throttling import SimpleRateThrottle
    api_settings.reload()
    SimpleRateThrottle.THROTTLE_RATES = api_settings.DEFAULT_THROTTLE_RATES
    try:
        for i in range(2):
            create_task(auth_client, image=image_file(color=(i, 0, 0)))
        response = auth_client.post(TASKS, {'file': image_file(color=(9, 9, 9))}, format='multipart')
        assert response.status_code == 429
        # listing is not throttled by the submission limit
        assert auth_client.get(TASKS).status_code == 200
    finally:
        api_settings.reload()
        SimpleRateThrottle.THROTTLE_RATES = api_settings.DEFAULT_THROTTLE_RATES


def test_deleting_a_task_removes_its_files(auth_client, fake_cellc2):
    """Deleted images must not stay reachable on disk/by URL (#23)."""
    data = create_task(auth_client)
    task = get_task(data['id'])
    task_dir = os.path.dirname(task.uploaded_image.path)
    assert os.path.isdir(task_dir)
    assert auth_client.delete('/api/v1/fs/' + data['id']).status_code == 204
    assert not os.path.exists(task_dir)


def test_deleting_a_folder_removes_task_files(auth_client, fake_cellc2):
    folder = create_folder(auth_client, 'A')
    task = get_task(create_task(auth_client, folder['id'])['id'])
    task_dir = os.path.dirname(task.uploaded_image.path)
    auth_client.delete('/api/v1/fs/' + folder['id'])
    assert not os.path.exists(task_dir)


def test_json_safe():
    from cell.tasks import json_safe
    value = {'a': np.int64(3), 'b': np.float32(0.5), 'c': np.array([1, 2]), 'd': float('nan'), 'e': (np.bool_(True),)}
    assert json_safe(value) == {'a': 3, 'b': 0.5, 'c': [1, 2], 'd': None, 'e': [True]}


def test_every_app_has_task_endpoints(auth_client):
    for prefix in ('a1', 'c1', 'c2', 'm1', 'm3', 'n1'):
        assert auth_client.get('/api/v1/cell/%s/tasks' % prefix).status_code == 200
