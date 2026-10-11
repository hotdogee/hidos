import io
import shutil
import zipfile

import pytest
from rest_framework.authtoken.models import Token

from conftest import PASSWORD, image_file
from fs.models import ChunkedUpload, File, Folder

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


# --- authentication (#96) -----------------------------------------------------

def test_anonymous_is_rejected(api_client):
    assert api_client.get(FS).status_code == 401
    assert api_client.post(FS, {'name': 'x'}, format='json').status_code == 401
    assert not File.objects.exists()


def test_session_is_not_enough_for_the_api(client, user):
    """The fs API is protected by tokens, a logged in session does not work (#96)."""
    client.force_login(user)
    assert client.get(FS).status_code == 401


def test_jwt_from_login_api_authorizes_fs(api_client, user):
    response = api_client.post('/api/v1/auth/login/', {'email': user.email, 'password': PASSWORD}, format='json')
    assert response.status_code == 200, response.content
    token = response.json()['token']
    api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
    assert api_client.get(FS).status_code == 200
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    assert api_client.get(FS).status_code == 200


def test_drf_token_authorizes_fs(api_client, user):
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    assert api_client.get(FS + 'home').status_code == 200


def test_invalid_jwt_is_rejected(api_client, user):
    api_client.credentials(HTTP_AUTHORIZATION='JWT not-a-token')
    assert api_client.get(FS).status_code == 401


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


def test_list_filter_and_optional_pagination(auth_client):
    """?limit/?offset paginate for infinite scrolling (#40); without them it is a plain list."""
    parent = create_folder(auth_client, 'Parent')
    for i in range(5):
        create_folder(auth_client, 'F%d' % i, parent['id'])
    assert len(auth_client.get(FS, {'folder': parent['id']}).json()) == 5
    page = auth_client.get(FS, {'folder': parent['id'], 'limit': 2, 'offset': 2}).json()
    assert page['count'] == 5
    assert len(page['results']) == 2
    assert page['next'] and page['previous']
    home_page = auth_client.get(FS + 'home', {'limit': 1}).json()
    assert home_page['count'] == 1


# --- batch download (#35) ---------------------------------------------------------

def test_batch_download_zip_of_results(auth_client, fake_cellc2):
    folder = create_folder(auth_client, 'Plate 1')
    t1 = create_task(auth_client, folder['id'], image_file('well A1.png', color=(1, 2, 3)))
    t2 = create_task(auth_client, None, image_file('b.png', color=(4, 5, 6)))
    response = auth_client.post(FS + 'download', {'ids': [folder['id'], t2['id']]}, format='json')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/zip'
    archive = zipfile.ZipFile(io.BytesIO(b''.join(response.streaming_content)))
    names = archive.namelist()
    assert 'results.csv' in names
    assert any(n.startswith('Plate 1/well A1_') and n.endswith('_result.png') for n in names)
    assert any(n.startswith('b_') and n.endswith('_result.png') for n in names)
    csv = archive.read('results.csv').decode()
    assert 'confluence' in csv and t1['id'] in csv and '12.34' in csv


def test_batch_download_only_includes_own_files(auth_client, other_client, fake_cellc2):
    task = create_task(auth_client)
    response = other_client.get(FS + 'download', {'ids': task['id']})
    assert response.status_code == 200
    archive = zipfile.ZipFile(io.BytesIO(b''.join(response.streaming_content)))
    assert archive.namelist() == ['results.csv']


def test_batch_download_rejects_bad_ids(auth_client):
    assert auth_client.get(FS + 'download', {'ids': 'nope'}).status_code == 400
    assert auth_client.get(FS + 'download').status_code == 400


# --- chunked resumable uploads (#56) ---------------------------------------------

def test_chunked_upload_resume_and_create_task(auth_client, user, fake_cellc2):
    data = image_file('big.png', size=(300, 200)).getvalue()
    upload = auth_client.post(FS + 'uploads', {'filename': 'big.png', 'size': len(data)}, format='json').json()
    url = FS + 'uploads/' + upload['id']
    half = len(data) // 2
    first = auth_client.put(url, data[:half], content_type='application/octet-stream',
                            HTTP_CONTENT_RANGE='bytes 0-%d/%d' % (half - 1, len(data)))
    assert first.status_code == 200 and first.json()['offset'] == half
    # a client that lost track of the offset gets 409 and the offset to resume from
    stale = auth_client.put(url, data[10:20], content_type='application/octet-stream',
                            HTTP_CONTENT_RANGE='bytes 10-19/%d' % len(data))
    assert stale.status_code == 409 and stale.json()['offset'] == half
    assert auth_client.get(url).json()['status'] == 'uploading'
    rest = auth_client.put(url, data[half:], content_type='application/octet-stream',
                           HTTP_CONTENT_RANGE='bytes %d-%d/%d' % (half, len(data) - 1, len(data)))
    assert rest.status_code == 200 and rest.json()['status'] == 'complete'

    response = auth_client.post('/api/v1/cell/c2/tasks', {'upload': upload['id']}, format='json')
    assert response.status_code == 201, response.content
    assert response.json()['name'] == 'big.png'
    assert not ChunkedUpload.objects.exists()


def test_incomplete_upload_cannot_create_task(auth_client):
    upload = auth_client.post(FS + 'uploads', {'filename': 'x.png', 'size': 100}, format='json').json()
    response = auth_client.post('/api/v1/cell/c2/tasks', {'upload': upload['id']}, format='json')
    assert response.status_code == 400


def test_uploads_are_private(auth_client, other_client):
    upload = auth_client.post(FS + 'uploads', {'filename': 'x.png', 'size': 10}, format='json').json()
    assert other_client.get(FS + 'uploads/' + upload['id']).status_code == 404
    assert other_client.put(FS + 'uploads/' + upload['id'], b'0123456789',
                            content_type='application/octet-stream').status_code == 404
    response = other_client.post('/api/v1/cell/c2/tasks', {'upload': upload['id']}, format='json')
    assert response.status_code == 400


def test_upload_size_limit(auth_client, settings):
    settings.CHUNKED_UPLOAD_MAX_BYTES = 10
    assert auth_client.post(FS + 'uploads', {'filename': 'x.png', 'size': 11}, format='json').status_code == 400


def test_abort_upload_removes_data(auth_client):
    upload = auth_client.post(FS + 'uploads', {'filename': 'x.png', 'size': 10}, format='json').json()
    path = ChunkedUpload.objects.get(pk=upload['id']).path
    assert auth_client.delete(FS + 'uploads/' + upload['id']).status_code == 204
    assert not ChunkedUpload.objects.exists()
    import os
    assert not os.path.exists(path)


def test_invalid_upload_data_is_rejected_and_kept_for_retry(auth_client):
    upload = auth_client.post(FS + 'uploads', {'filename': 'x.png', 'size': 10}, format='json').json()
    auth_client.put(FS + 'uploads/' + upload['id'], b'0123456789', content_type='application/octet-stream')
    response = auth_client.post('/api/v1/cell/c2/tasks', {'upload': upload['id']}, format='json')
    assert response.status_code == 400
    # the file is closed again, so the upload can still be deleted
    assert auth_client.delete(FS + 'uploads/' + upload['id']).status_code == 204


def test_cleanup_uploads_command(auth_client, settings):
    import datetime
    import os
    from django.core.management import call_command
    old = auth_client.post(FS + 'uploads', {'filename': 'old.png', 'size': 10}, format='json').json()
    new = auth_client.post(FS + 'uploads', {'filename': 'new.png', 'size': 10}, format='json').json()
    ChunkedUpload.objects.filter(pk=old['id']).update(created=ChunkedUpload.objects.get(pk=old['id']).created - datetime.timedelta(days=2))
    old_path = ChunkedUpload.objects.get(pk=old['id']).path
    call_command('cleanup_uploads')
    assert list(ChunkedUpload.objects.values_list('filename', flat=True)) == ['new.png']
    assert not os.path.exists(old_path)
