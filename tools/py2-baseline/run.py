# Runs every analysis app on its example image (and on every other image
# given) and prints the results as JSON. Works with the 2016 Python 2.7 code
# and with the ported code.
#
#   python run.py <hidos-django/hidos of the code to run> <hidos-django/hidos with the Example images> \
#       [out.json] [image ...]
from __future__ import print_function
import glob
import json
import os
import shutil
import sys
import tempfile
import types
import importlib

src, examples = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3].endswith('.json') else None
extra_images = sys.argv[4 if out else 3:]
sys.path.insert(0, src)
try:
    from django.conf import settings
    if not settings.configured:
        settings.configure()
except ImportError:  # the 2016 code only imports django.conf.settings
    django = types.ModuleType('django')
    django.conf = types.ModuleType('django.conf')
    django.conf.settings = type('Settings', (), {})()
    sys.modules['django'] = django
    sys.modules['django.conf'] = django.conf


class F(object):
    def __init__(self, path):
        self.path = path


class Record(object):
    def __init__(self, uploaded, workdir):
        self.name = os.path.basename(uploaded)
        self.uploaded_image = F(uploaded)
        self.result_image = F(os.path.join(workdir, 'result' + os.path.splitext(uploaded)[1].lower()))
        self.result_display = F(os.path.join(workdir, 'result_display.jpg'))


def plain(value):
    return json.loads(json.dumps(value, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o)))


APPS = ('cella1', 'cellc1', 'cellc2', 'cellm1', 'cellm3', 'celln1')
runs = []
for app_name in APPS:
    image = [p for p in glob.glob(os.path.join(examples, app_name, 'static', app_name, 'images', 'Example.*'))
             if not p.endswith('.json')][0]
    runs.append((app_name, app_name, image))
for image in extra_images:
    runs.extend((os.path.basename(image) + ' ' + app_name, app_name, image) for app_name in APPS)

results = {}
for key, app_name, image in runs:
    workdir = tempfile.mkdtemp()
    try:
        results[key] = plain(importlib.import_module(app_name).run(Record(image, workdir)))
    finally:
        shutil.rmtree(workdir)
    print(key, json.dumps(results[key], sort_keys=True))
    sys.stdout.flush()
if out:
    with open(out, 'w') as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
