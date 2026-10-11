import shutil

import pytest

from conftest import image_file
from fs.models import File, Folder

pytestmark = pytest.mark.django_db

FS = '/api/v1/fs/'


def fake_run(result=None):
    """Stand-in for an analysis algorithm: copies the input as the result."""
    def run(task_record):
        shutil.copyfile(task_record.uploaded_display.path, task_record.result_image.path)
        shutil.copyfile(task_record.uploaded_display.path, task_record.result_display.path)
        return result if result is not None else {'confluence': '12.34'}
    return run


@pytest.fixture
def fake_cellc2(monkeypatch):
    import cellc2
    monkeypatch.setattr(cellc2, 'run', fake_run())


def create_folder(client, name, folder=None):
    data = {'name': name}
    if folder is not None:
        data['folder'] = folder
    response = client.post(FS, data, format='json')
    assert response.status_code == 201, response.content
    return response.json()


def create_task(client, folder=None, image=None):
    data = {'file': image or image_file()}
    if folder is not None:
        data['folder'] = folder
    response = client.post('/api/v1/cell/c2/tasks', data, format='multipart')
    assert response.status_code == 201, response.content
    return response.json()


# --- folders --------------------------------------------------------------------

def test_create_folder_in_home_without_folder_field(auth_client, user):
    folder = create_folder(auth_client, 'Experiments')
    assert folder['folder'] is None
    assert folder['owner'] == user.pk
    home = auth_client.get(FS + 'home').json()
    assert home['name'] == 'Home'
    assert [f['id'] for f in home['files']] == [folder['id']]


def test_nested_folder_path_and_breadcrumbs(auth_client):
    parent = create_folder(auth_client, 'A')
    child = create_folder(auth_client, 'B', parent['id'])
    data = auth_client.get(FS + child['id']).json()
    assert data['folder'] == parent['id']
    assert data['path'] == 'Home/A/B'
    assert data['breadcrumbs'] == [['Home', 'Home'], [parent['id'], 'A']]


def test_patch_rename_without_folder_attribute(auth_client):
    """PATCH with only `name` used to fail with a KeyError on `folder` (#97)."""
    parent = create_folder(auth_client, 'A')
    child = create_folder(auth_client, 'B', parent['id'])
    response = auth_client.patch(FS + child['id'], {'name': 'Renamed'}, format='json')
    assert response.status_code == 200, response.content
    assert response.json()['name'] == 'Renamed'
    assert response.json()['folder'] == parent['id']


def test_patch_move_to_home_with_null_folder(auth_client):
    parent = create_folder(auth_client, 'A')
    child = create_folder(auth_client, 'B', parent['id'])
    response = auth_client.patch(FS + child['id'], {'folder': None}, format='json')
    assert response.status_code == 200
    assert Folder.objects.get(pk=child['id']).folder is None


def test_cannot_move_folder_into_itself_or_a_subfolder(auth_client):
    a = create_folder(auth_client, 'A')
    b = create_folder(auth_client, 'B', a['id'])
    c = create_folder(auth_client, 'C', b['id'])
    assert auth_client.patch(FS + a['id'], {'folder': a['id']}, format='json').status_code == 400
    assert auth_client.patch(FS + a['id'], {'folder': c['id']}, format='json').status_code == 400
    assert Folder.objects.get(pk=a['id']).folder is None


def test_folder_name_validation(auth_client):
    assert auth_client.post(FS, {'name': 'a/b'}, format='json').status_code == 400
    assert auth_client.post(FS, {'name': ''}, format='json').status_code == 400


def test_users_only_see_their_own_files(auth_client, other_client):
    mine = create_folder(auth_client, 'Mine')
    assert other_client.get(FS).json() == []
    assert other_client.get(FS + mine['id']).status_code == 404
    assert other_client.patch(FS + mine['id'], {'name': 'x'}, format='json').status_code == 404
    assert other_client.delete(FS + mine['id']).status_code == 404
    assert Folder.objects.filter(pk=mine['id']).exists()


def test_cannot_create_inside_someone_elses_folder(auth_client, other_client):
    mine = create_folder(auth_client, 'Mine')
    response = other_client.post(FS, {'name': 'Intruder', 'folder': mine['id']}, format='json')
    assert response.status_code == 400
    assert 'folder' in response.json()


def test_delete_folder_deletes_contents(auth_client, fake_cellc2):
    folder = create_folder(auth_client, 'A')
    task = create_task(auth_client, folder['id'])
    assert auth_client.delete(FS + folder['id']).status_code == 204
    assert not File.objects.filter(pk__in=[folder['id'], task['id']]).exists()
