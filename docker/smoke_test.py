"""
End-to-end check of a running docker compose stack (used by CI, works locally):

    docker compose up -d --wait
    python docker/smoke_test.py [http://localhost:8080]

Creates a verified user, logs in through the REST API, uploads the Cell C2
example image, waits for the Celery worker to run the real analysis and
checks the result, the result image and the batch download. Standard
library only.
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:%s' % os.environ.get('HIDOS_PORT', '8080')).rstrip('/')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE = os.path.join(ROOT, 'hidos-django', 'hidos', 'cellc2', 'static', 'cellc2', 'images', 'Example.jpg')
EMAIL = 'smoke-%s@example.com' % uuid.uuid4().hex[:8]
PASSWORD = uuid.uuid4().hex


def request(method, path, data=None, headers=None, raw=False):
    headers = dict(headers or {})
    body = None
    if isinstance(data, dict):
        body = json.dumps(data).encode()
        headers['Content-Type'] = 'application/json'
    elif data is not None:
        body = data
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            content = response.read()
            return response.status, (content if raw else json.loads(content or b'null'))
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def multipart(field, filename, content):
    boundary = uuid.uuid4().hex
    body = (('--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\n'
             'Content-Type: application/octet-stream\r\n\r\n') % (boundary, field, filename)).encode()
    body += content + ('\r\n--%s--\r\n' % boundary).encode()
    return body, {'Content-Type': 'multipart/form-data; boundary=' + boundary}


def check(condition, message):
    if not condition:
        print('FAIL:', message)
        sys.exit(1)
    print('ok  ', message)


status, data = request('GET', '/healthz')
check(status == 200 and data == {'status': 'ok'}, 'health check')
status, html = request('GET', '/cell/', raw=True)
check(status == 200 and b'Cell Cloud' in html and b'Cell S<' not in html, 'landing page')
status, _ = request('GET', '/api/v1/fs/')
check(status == 401, 'API requires a token')
status, examples = request('GET', '/api/v1/cell/examples')
check(status == 200 and len(examples) == 6, 'examples API')

script = ("from allauth.account.models import EmailAddress; from users.models import User; "
          "u = User.objects.create_user(email='%s', password='%s'); "
          "EmailAddress.objects.create(user=u, email=u.email, verified=True, primary=True)" % (EMAIL, PASSWORD))
subprocess.run(['docker', 'compose', 'exec', '-T', 'web', 'python', 'manage.py', 'shell', '-c', script],
               cwd=ROOT, check=True)
status, login = request('POST', '/api/v1/auth/login/', {'email': EMAIL, 'password': PASSWORD})
check(status == 200 and login.get('token'), 'login returns a JWT')
auth = {'Authorization': 'JWT ' + login['token']}

status, folder = request('POST', '/api/v1/fs/', {'name': 'Smoke test'}, auth)
check(status == 201 and folder['folder'] is None, 'create a folder in Home')
with open(EXAMPLE, 'rb') as fh:
    body, headers = multipart('file', 'example.jpg', fh.read())
status, task = request('POST', '/api/v1/cell/c2/tasks', body, dict(auth, **headers))
check(status == 201, 'submit a Cell C2 task in Home (%s)' % status)

deadline = time.time() + 300
while True:
    status, item = request('GET', '/api/v1/fs/' + task['id'], headers=auth)
    state = item['content']['status']
    if state not in ('queued', 'running') or time.time() > deadline:
        break
    time.sleep(2)
check(state == 'success', 'worker ran the analysis (status %s)' % state)
check(item['content']['result'] == {'confluence': '25.66'}, 'result matches the 2016 reference (%s)' % item['content']['result'])
status, image = request('GET', item['content']['result_display'], raw=True)
check(status == 200 and image[:2] == b'\xff\xd8', 'result image served by nginx')
status, thumb = request('GET', item['content']['thumbnail'], raw=True)
check(status == 200 and thumb[:2] == b'\xff\xd8', 'thumbnail')
status, archive = request('GET', '/api/v1/fs/download?ids=' + task['id'], headers=auth, raw=True)
check(status == 200 and archive[:2] == b'PK', 'batch download zip')
status, _ = request('PATCH', '/api/v1/fs/' + folder['id'], {'name': 'Renamed'}, auth)
check(status == 200, 'rename a folder with PATCH')
status, _ = request('DELETE', '/api/v1/fs/' + task['id'], headers=auth)
check(status == 204, 'delete the task')
print('smoke test passed')
