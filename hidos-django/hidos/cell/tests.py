import os

import numpy as np
import pytest
from PIL import Image

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


def test_task_representation_through_fs_api(auth_client, fake_cellc2):
    data = create_task(auth_client)
    item = auth_client.get('/api/v1/fs/' + data['id']).json()
    content = item['content']
    assert content['status'] == 'success'
    assert content['result'] == {'confluence': 12.5, 'count': 3}
    for key in ('uploaded_image', 'uploaded_display', 'result_image', 'result_display', 'thumbnail'):
        assert content[key].startswith('/media/cellc2/task/'), key


def test_thumbnail_is_created(auth_client, settings, fake_cellc2):
    """Every upload gets a small JPEG preview (#38)."""
    settings.THUMBNAIL_SIZE = 32
    task = get_task(create_task(auth_client, image=image_file(size=(200, 100)))['id'])
    with Image.open(task.thumbnail.path) as thumb:
        assert thumb.format == 'JPEG'
        assert thumb.size == (32, 16)
    with Image.open(task.uploaded_display.path) as display:
        assert display.format == 'JPEG' and display.size == (200, 100)


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


def test_duplicate_upload_returns_existing_task(auth_client, monkeypatch, fake_cellc2):
    import cellc2
    first = create_task(auth_client)
    runs = []
    monkeypatch.setattr(cellc2, 'run', lambda record: runs.append(1) or {})
    second = create_task(auth_client)
    assert second['id'] == first['id']
    assert runs == []  # already analyzed, not queued again
    assert File.objects.count() == 1


def test_resubmitting_a_failed_image_runs_it_again(auth_client, monkeypatch):
    import cellc2
    monkeypatch.setattr(cellc2, 'run', lambda record: 1 / 0)
    first = create_task(auth_client)
    assert get_task(first['id']).status == 'failed'
    monkeypatch.setattr(cellc2, 'run', fake_run())
    create_task(auth_client)
    assert get_task(first['id']).status == 'success'


def test_same_image_from_two_users_gives_two_tasks(auth_client, other_client, fake_cellc2):
    a = create_task(auth_client)
    b = create_task(other_client)
    assert a['id'] != b['id']


def test_task_ids_depend_on_secret_key(settings, user):
    from cell.models import task_id_for
    a = task_id_for('cellc2', '0.8', user, b'image')
    settings.SECRET_KEY = 'another-secret-key-for-this-test-only-123456'
    assert task_id_for('cellc2', '0.8', user, b'image') != a
    assert len(a) == 32


def test_same_image_in_two_apps_with_the_same_version_gives_two_tasks(auth_client, monkeypatch):
    """Cell A1 and Cell C1 are both version 0.30; their task ids used to collide (HTTP 500)."""
    import cella1
    import cellc1
    assert cella1.version == cellc1.version
    monkeypatch.setattr(cella1, 'run', fake_run({'#Mesh': 1}))
    monkeypatch.setattr(cellc1, 'run', fake_run({'count': 1}))
    a1 = auth_client.post('/api/v1/cell/a1/tasks', {'file': image_file()}, format='multipart')
    c1 = auth_client.post('/api/v1/cell/c1/tasks', {'file': image_file()}, format='multipart')
    assert a1.status_code == 201 and c1.status_code == 201, (a1.content, c1.content)
    assert a1.json()['id'] != c1.json()['id']
    assert File.objects.count() == 2


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


def test_running_and_list_endpoints(auth_client, other_client, fake_cellc2):
    create_task(auth_client)
    assert len(auth_client.get(TASKS).json()) == 1
    assert auth_client.get(TASKS + '/running').json() == []
    assert other_client.get(TASKS).json() == []


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


def test_examples_api_is_public(api_client):
    """#43"""
    response = api_client.get('/api/v1/cell/examples')
    assert response.status_code == 200
    examples = {e['app']: e for e in response.json()}
    assert set(examples) == {'cella1', 'cellc1', 'cellc2', 'cellm1', 'cellm3', 'celln1'}
    for e in examples.values():
        assert e['uploaded_image'].startswith('/static/%s/images/Example.' % e['app'])
        assert e['result_image'] == '/static/%s/images/Example_r.jpg' % e['app']
        assert isinstance(e['result'], dict) and e['result']


def test_every_app_has_task_endpoints(auth_client):
    for prefix in ('a1', 'c1', 'c2', 'm1', 'm3', 'n1'):
        assert auth_client.get('/api/v1/cell/%s/tasks' % prefix).status_code == 200


def corrupt_png():
    """A PNG whose chunk CRCs are valid (Pillow's verify() passes) but whose pixel data is not."""
    import struct
    import zlib
    data = image_file(size=(32, 32)).getvalue()
    i = data.index(b'IDAT')
    length = struct.unpack('>I', data[i - 4:i])[0]
    payload = b'\x00' * length
    chunk = b'IDAT' + payload
    return data[:i] + chunk + struct.pack('>I', zlib.crc32(chunk) & 0xffffffff) + data[i + 4 + length + 4:]


def test_undecodable_image_is_rejected_without_leaving_a_task(auth_client, settings):
    """It used to answer 500 and leave a 'queued' task that was never analyzed."""
    upload = image_file()
    upload = type(upload)(corrupt_png())
    upload.name = 'broken.png'
    response = auth_client.post(TASKS, {'file': upload}, format='multipart')
    assert response.status_code == 400, response.content
    assert 'file' in response.json()
    assert not File.objects.exists()
    assert not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'cellc2', 'task')) or \
        not os.listdir(os.path.join(settings.MEDIA_ROOT, 'cellc2', 'task'))


def test_email_change_does_not_hand_over_tasks(auth_client, other_client, user, other_user, fake_cellc2):
    first = create_task(auth_client)
    old_email = user.email
    user.email = 'alice.new@example.com'
    user.save()
    other_user.email = old_email
    other_user.save()
    second = create_task(other_client)
    assert second['id'] != first['id']
    assert second['owner'] == other_user.pk
    assert get_task(first['id']).owner == user


def test_rename_during_analysis_is_kept(auth_client, monkeypatch):
    import cellc2
    run = fake_run()

    def renaming_run(task_record):
        File.objects.filter(pk=task_record.pk).update(name='renamed while running')
        return run(task_record)
    monkeypatch.setattr(cellc2, 'run', renaming_run)
    task = get_task(create_task(auth_client)['id'])
    assert task.status == 'success'
    assert task.name == 'renamed while running'


def test_task_deleted_during_analysis_stays_deleted(auth_client, monkeypatch):
    import cellc2
    run = fake_run()

    def deleting_run(task_record):
        File.objects.filter(pk=task_record.pk).delete()
        return run(task_record)
    monkeypatch.setattr(cellc2, 'run', deleting_run)
    response = auth_client.post(TASKS, {'file': image_file()}, format='multipart')
    assert response.status_code == 201
    assert not File.objects.exists()


def test_api_shows_only_the_last_line_of_errors(auth_client, monkeypatch):
    import cellc2
    monkeypatch.setattr(cellc2, 'run', lambda record: 1 / 0)
    data = create_task(auth_client)
    content = auth_client.get('/api/v1/fs/' + data['id']).json()['content']
    assert content['status'] == 'failed'
    assert content['error'] == 'ZeroDivisionError: division by zero'
    assert 'Traceback' in get_task(data['id']).error
