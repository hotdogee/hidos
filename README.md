# HiDOS

[![CI](https://github.com/hotdogee/hidos/actions/workflows/ci.yml/badge.svg)](https://github.com/hotdogee/hidos/actions/workflows/ci.yml)
![Python 3.12 | 3.13 | 3.14](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-blue)
![Django 5.2 LTS](https://img.shields.io/badge/django-5.2%20LTS-0C4B33)

HiDOS bioinformatics platform.

## Cell Cloud

*Instant cell image analysis for modern biologists.*

Cell Cloud is a web platform where biologists upload microscope images and
get them analyzed: cells counted, confluence measured, tube formation and
neurite outgrowth quantified. Uploads are organized in folders, analyses run
in a background queue, and each result comes back as numbers plus an
annotated result image.

| App | Measures | Version | Example input | Example result |
| --- | --- | --- | --- | --- |
| **Cell A1** (`cella1`) | Angiogenesis / tube formation: junctions, meshes, segments, branches | 0.3 | <img src="hidos-django/hidos/cella1/static/cella1/images/Example.jpg" width="160"> | <img src="hidos-django/hidos/cella1/static/cella1/images/Example_r.jpg" width="160"> |
| **Cell C1** (`cellc1`) | Cell count | 0.3 | <img src="hidos-django/hidos/cellc1/static/cellc1/images/Example.png" width="160"> | <img src="hidos-django/hidos/cellc1/static/cellc1/images/Example_r.jpg" width="160"> |
| **Cell C2** (`cellc2`) | Confluence | 0.8 | <img src="hidos-django/hidos/cellc2/static/cellc2/images/Example.jpg" width="160"> | <img src="hidos-django/hidos/cellc2/static/cellc2/images/Example_r.jpg" width="160"> |
| **Cell M1** (`cellm1`) | Transwell migration assay (stained area ratio) | 0.2 | <img src="hidos-django/hidos/cellm1/static/cellm1/images/Example.jpg" width="160"> | <img src="hidos-django/hidos/cellm1/static/cellm1/images/Example_r.jpg" width="160"> |
| **Cell M3** (`cellm3`) | Migration (wound area ratio) | 0.2 | <img src="hidos-django/hidos/cellm3/static/cellm3/images/Example.jpg" width="160"> | <img src="hidos-django/hidos/cellm3/static/cellm3/images/Example_r.jpg" width="160"> |
| **Cell N1** (`celln1`) | Neurite outgrowth: cell bodies, branches, outgrowth length | 0.5 | <img src="hidos-django/hidos/celln1/static/celln1/images/Example.jpg" width="160"> | <img src="hidos-django/hidos/celln1/static/celln1/images/Example_r.jpg" width="160"> |

The result images and numbers above are produced by
`python manage.py generate_examples` and served by the examples API.

## Quick start (docker compose)

Requires Docker with the compose plugin.

```sh
git clone https://github.com/hotdogee/hidos.git
cd hidos
cp .env.example .env
# set DJANGO_SECRET_KEY in .env, e.g. python -c "import secrets; print(secrets.token_urlsafe(50))"
docker compose up -d --build --wait
docker compose exec web python manage.py createsuperuser
```

Then open:

* <http://localhost:8080/cell/>: landing page
* <http://localhost:8080/admin/>: Django admin
* `http://localhost:8080/api/v1/...`: REST API (see [REST API](#rest-api))
* <http://localhost:8080/login>: login page; after logging in, results are
  viewable at `/results/<task id>`

The stack is nginx, the Django web app (gunicorn), a Celery worker running the
analyses, the landing page (`hidos-express`), PostgreSQL and RabbitMQ. Data
lives in named volumes (`pgdata`, `media`, ...); `docker/backup.sh` backs up
the database and the uploaded images (see [Backups](#backups)).
`python docker/smoke_test.py` runs an end-to-end check against a running stack.

## Manual development setup

Works on Linux, macOS and Windows. You need:

* Python 3.12, 3.13 or 3.14
* PostgreSQL 13+ (SQLite works for the test suite only)
* RabbitMQ, or set `CELERY_TASK_ALWAYS_EAGER=true` to run analyses inside the
  web process during development
* No compilers: NumPy, SciPy, scikit-image, mahotas and OpenCV install as
  wheels (the old `install_opencv.sh` and `lib\win64` wheels aren't needed
  any more)

```sh
cd hidos-django/hidos
python -m venv env                  # Windows: py -3 -m venv env
. env/bin/activate                  # Windows: env\Scripts\activate
pip install -r requirements/local.txt
cp ../../.env.example .env          # the settings read hidos-django/hidos/.env
```

Create the database (the default `DATABASE_URL` is `postgres://django@localhost:5432/django`):

```sh
createuser -s -U postgres django
createdb -U postgres --owner django django
```

Then:

```sh
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver                      # http://127.0.0.1:8000/
celery -A hidos worker --loglevel=info -Q cell  # in a second shell; add --pool=solo on Windows
```

`hidos.settings.local` is the default settings module: debug on, browsable
API with session login, logs in `../../log/`. On Windows the original helper
scripts in `hidos-django/` (`init_venv.cmd`, `setup_postgres.cmd`,
`run_server.cmd`, `run_celery.cmd`, ...) still work and use the same `env`
virtualenv. The 2016 Windows / Python 2.7 guide is kept in
[docs/legacy-windows-setup.md](docs/legacy-windows-setup.md).

VS Code launch configurations for the server, the worker and the tests are
in `.vscode/launch.json`.

## Configuration

All deployment settings come from environment variables (or a `.env` file).
[.env.example](.env.example) lists all of them. The important ones:

| Variable | Default | |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | none | **Required in production.** |
| `DJANGO_SETTINGS_MODULE` | `hidos.settings.local` | `hidos.settings.production` in the Docker image |
| `DJANGO_ALLOWED_HOSTS` | `.hidos.io` | Comma separated |
| `CSRF_TRUSTED_ORIGINS` | `https://*.hidos.io` | Origins that may POST forms (admin, login) |
| `DATABASE_URL` | `postgres://django@localhost:5432/django` | |
| `CELERY_BROKER_URL` | `amqp://guest:guest@localhost:5672//` | |
| `EMAIL_URL` | `consolemail://` | e.g. `smtp+tls://user:password@smtp.example.com:587` |
| `SITE_DOMAIN` | `hidos.io` | Used in account emails |
| `CORS_ALLOWED_ORIGINS` | none | Origin(s) of the single page app |
| `API_SESSION_AUTH` | `false` (`true` in local settings) | Allow browser sessions on the API |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`, `FACEBOOK_CLIENT_ID` / `FACEBOOK_CLIENT_SECRET` | none | Social login. Alternatively add *Social applications* in the admin ([docs/social-login.md](docs/social-login.md)) |
| `SLACK_WEBHOOK_URL` | none | Post failed analyses to Slack |
| `GOOGLE_ANALYTICS_ID` | none | Google Analytics on the Django pages and the landing page; off when empty |
| `MEDIA_ROOT` | `hidos-django/hidos/media` | Uploaded images and results |
| `THROTTLE_*` | see `.env.example` | Rate limits, e.g. `THROTTLE_TASK_SUBMIT=600/h` |

## Architecture

```mermaid
flowchart LR
    browser([Browser / SPA]) --> nginx
    nginx -- "/cell/" --> landing["hidos-express<br/>landing page"]
    nginx -- "/media/" --> media[(media volume)]
    nginx -- "/api, /admin, /accounts, ..." --> web["Django + DRF<br/>(gunicorn)"]
    web --> db[(PostgreSQL)]
    web -- "analysis(task id)" --> broker[(RabbitMQ)]
    broker --> worker["Celery worker<br/>OpenCV, scikit-image, mahotas"]
    worker --> db
    web --> media
    worker --> media
```

* **`hidos-django/hidos`** is the Django project (`hidos/settings/{base,local,production,staging,test}.py`).
  * `fs` is the per-user file system. Every item is a `File`; `Folder` and the
    analysis tasks are subclasses of it (multi-table inheritance), and
    `File.content` points to the concrete object. `folder=None` is the
    user's *Home* folder.
  * `cell` is the shared task model, upload manager, REST viewset and Celery
    task base class (`cell/tasks.py`). It also has `cell/skimage_compat.py`
    and `cell/pymorph.py`, which keep the algorithms' 2016 numerical
    behavior on current NumPy, scikit-image and OpenCV (see
    [Development](#development)).
  * `cella1`, `cellc1`, `cellc2`, `cellm1`, `cellm3`, `celln1` are the
    analysis apps. Each has a `Task` model, its REST endpoints and the
    algorithm in `bin/` (`bin/__init__.py` picks the active version; older
    versions and the R prototypes are kept next to it).
  * `users` is the custom user model: email as the account name, plus
    organization, language and profile image. It includes the auth
    serializers for dj-rest-auth and django-allauth.
  * `app` holds the server-rendered pages: login, the result viewer, the
    health check and the sites data migration.
* **`hidos-express`** is the static landing page (Express 5 + helmet).
* **`tools/`** has the original R and notebook prototypes, test images, the
  2016 nginx configuration for hidos.io, logos, and
  [tools/py2-baseline](tools/py2-baseline) for reproducing the 2016 results.

An upload is stored under `MEDIA_ROOT/<app>/task/<task id>/`, together with a
JPEG copy for display and a thumbnail. Then a Celery task runs the app's
algorithm, stores the numbers in `Task.result` (JSON), and writes the result
image. The task status goes `queued` → `running` → `success` or `failed`
(with the traceback in `Task.error`). Uploading the same image twice
returns the existing task.

## REST API

All endpoints except the examples need a token: either a JWT from the login
endpoint (`Authorization: JWT <token>` or `Bearer <token>`), or a DRF token
created in the admin (`Authorization: Token <key>`).

| Endpoint | |
| --- | --- |
| `POST /api/v1/auth/registration/` | Sign up (email confirmation required) |
| `POST /api/v1/auth/login/` | `{email, password}` returns `{token, access, refresh, user}` |
| `POST /api/v1/auth/token/refresh/` | New access token |
| `POST /api/v1/auth/google/`, `/api/v1/auth/facebook/` | Social login with a provider access token |
| `GET/PATCH /api/v1/auth/user/` | Profile: name, organization, language, image |
| `GET /api/v1/fs/home` | Home folder and its contents (`?limit=&offset=` paginates) |
| `GET/POST /api/v1/fs/` | List (`?folder=<id>`, `?type=`, `?limit=`) or create folders |
| `GET/PATCH/DELETE /api/v1/fs/<id>` | Folder or task: rename, move (`folder`), delete |
| `GET/POST /api/v1/fs/download` | Zip of the result images (and `results.csv`) of the selected ids |
| `POST /api/v1/fs/uploads`, `PUT/GET/DELETE /api/v1/fs/uploads/<id>` | Chunked, resumable uploads (see `fs/uploads.py`) |
| `GET/POST /api/v1/cell/<a1, c1, c2, m1, m3 or n1>/tasks` | List or submit tasks (`file` or `upload`, optional `folder`) |
| `GET/DELETE /api/v1/cell/<app>/tasks/<id>`, `GET .../tasks/running` | Task detail, running tasks |
| `GET /api/v1/cell/examples` | Example images and results of every app (public) |

In local development the browsable API at <http://127.0.0.1:8000/api/v1/fs/>
works after logging in at `/login`.

## Development

```sh
cd hidos-django/hidos
pip install -r requirements/test.txt
pytest                          # everything, about a minute
pytest -m "not analysis"        # skip the real image analysis tests
ruff check .
python manage.py makemigrations --check --dry-run
cd ../../hidos-express && npm ci && npm test
```

The tests use SQLite unless `DATABASE_URL` is set; CI runs them against
PostgreSQL on Python 3.12, 3.13 and 3.14. Celery runs eagerly in the tests.

`cell/test_analysis.py` runs every algorithm on its example image and on two
colour photos (`cell/testdata`). It checks that the results equal what the
original Python 2.7 / scikit-image 0.12 / OpenCV 3 stack produced in 2016.
The exceptions are Cell M1 on its example, whose JPEG decodes slightly
differently today, and Cell M1 on one of the photos, where the 2016 number
depended on the CPU (details in [tools/py2-baseline](tools/py2-baseline)).
`tools/py2-baseline` rebuilds that 2016 environment in Docker. Reproducing
the old numbers needed a few compatibility shims for library changes since
2016, collected in `cell/skimage_compat.py`:

* thresholds of `remove_small_objects` and `remove_small_holes`
* `resize` defaults, with an exact scaling matrix
* edge filter borders and 0.12's integer to float conversion
* the 0.12 `canny`
* OpenCV 3's `GaussianBlur` and colour to grey conversion
* Python 2 rounding, also with digits (`round(x, 3)`)

The shims avoid library functions whose last bits depend on the CPU, so the
algorithms give the same numbers on Linux and Windows, with or without
AVX-512.

pymorph has no Python 3 release, so the functions the algorithms use are
ported in `cell/pymorph.py`.

GitHub Actions ([.github/workflows/ci.yml](.github/workflows/ci.yml)) runs
three jobs:

* the Django tests, lint and migration checks
* the landing page tests
* a Docker build and compose end-to-end smoke test

Dependabot proposes grouped dependency updates once a month.

## Deployment

The compose file is the reference deployment. For production:

* set a strong `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`,
  `CSRF_TRUSTED_ORIGINS`, `EMAIL_URL`, and new database and broker passwords
* terminate TLS in front of nginx (the 2016 hidos.io setup is in
  `tools/nginx`) and set `SESSION_COOKIE_SECURE=true` and
  `CSRF_COOKIE_SECURE=true`
* set `NUM_PROXIES` to the number of proxies in front of Django (1 in the
  compose file for nginx; 2 with a TLS proxy in front of it), so rate
  limits use the real client address
* run `python manage.py check --deploy` with the production settings
* run `python manage.py cleanup_uploads` daily (cron, or
  `docker compose exec web ...`) to delete abandoned chunked uploads

Uploaded images and results under `/media/` are served by nginx without a
login, like in the 2016 deployment. The paths contain the task id, which is
keyed with `DJANGO_SECRET_KEY` and can't be guessed. If images must only be
visible to their owner, serve media through Django with nginx
`X-Accel-Redirect` (an owner decision; it changes how clients load images).

### Backups

`docker/backup.sh [dir]` writes a PostgreSQL dump and a tarball of the media
volume into a timestamped directory; the script's header lists the restore
commands. Run it from cron and copy the result off the machine. For
redundancy, put the `media` and `pgdata` volumes on replicated storage (RAID,
a network file system, or an object store mounted for `MEDIA_ROOT`).

## Roadmap

The [issue list](https://github.com/hotdogee/hidos/issues) is the 2016 to-do
list.

**Done in the 2026 maintenance pass:**

* Python 3 / Django 5.2 port
* CI (#28)
* docker compose deployment (#5)
* logging and failed-task status (#12)
* permissions and security review (#15, #16, #23)
* local and social signup (#18, #19)
* social accounts merged by email (#67)
* rate limiting (#26)
* user profile model, serializer and API (#74, #75, #76)
* sites migration (#78)
* token-protected API (#96)
* fs fixes (#97, #98)
* thumbnails (#38)
* batch download (#35)
* chunked uploads (#56)
* examples (#43, #44)
* result viewer fit-to-image (#66)
* landing page: responsive menu, Cell S removed (#48, #57)
* optional Google Analytics (#13, #14)

**Backend ready, frontend pending:** infinite scrolling (#40) and task
selection (#30). The single page app is not part of this repository.

**Open:**

* payments (#9, #10, #11; see [docs/payments.md](docs/payments.md))
* PDF reports (#39)
* the remaining UI work on the single page app
* replicated storage (#24)

## History and credits

HiDOS Cell Cloud was built in 2016 at Meridigen by:

* **Han Lin** ([@hotdogee](https://github.com/hotdogee)): architecture,
  Django backend, file system and REST APIs
* **Weian Wang** ([@Weiweiann](https://github.com/Weiweiann)): the analysis
  apps' integration and web interface, social login, deployment
* **Aaron Lin**: the Cell A, C1 and C2 algorithms
* **Ira** ([@irashadow](https://github.com/irashadow)): Cell M1 and M3
* **yushi0223**: Cell C1 and C2 fixes
* **Tsung-jui Chen**: web app work

The first versions of each app lived in their own branches (`cellc1`,
`cellc2`, `cellm`, `cells`, ...); `cellbase` is where they were moved onto
the shared fs and REST architecture. The 2016 presentation is in
`hidos-express/tools/presentation/`.

The repository has no license file yet.
