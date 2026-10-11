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


def test_create_task_in_folder(auth_client, fake_cellc2):
    folder = create_folder(auth_client, 'Plate')
    data = create_task(auth_client, folder['id'])
    assert data['folder'] == folder['id']
    listed = auth_client.get('/api/v1/fs/' + folder['id']).json()['files']
    assert [f['id'] for f in listed] == [data['id']]


def test_invalid_upload_is_rejected(auth_client):
    bad = image_file()
    bad = type(bad)(b'not an image')
    bad.name = 'x.png'
    assert auth_client.post(TASKS, {'file': bad}, format='multipart').status_code == 400
    assert auth_client.post(TASKS, {}, format='multipart').status_code == 400
    assert not File.objects.exists()


def test_json_safe():
    from cell.tasks import json_safe
    value = {'a': np.int64(3), 'b': np.float32(0.5), 'c': np.array([1, 2]), 'd': float('nan'), 'e': (np.bool_(True),)}
    assert json_safe(value) == {'a': 3, 'b': 0.5, 'c': [1, 2], 'd': None, 'e': [True]}


def test_every_app_has_task_endpoints(auth_client):
    for prefix in ('a1', 'c1', 'c2', 'm1', 'm3', 'n1'):
        assert auth_client.get('/api/v1/cell/%s/tasks' % prefix).status_code == 200
