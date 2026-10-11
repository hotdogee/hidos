"""
Example images of the analysis apps (#43, #44).

Every app keeps its example input in <app>/static/<app>/images/Example.<ext>;
`manage.py generate_examples` runs the app on it and writes Example_r.jpg
(the result image) and Example.json (the numbers) next to it.
"""
import glob
import json
import os
import sys

from django.apps import apps
from django.templatetags.static import static


def analysis_apps():
    """AppConfigs of the installed analysis apps (cella1, cellc1, ...)"""
    from .models import CellTask
    found = []
    for config in apps.get_app_configs():
        module = sys.modules.get(config.name)
        task = config.models_module and getattr(config.models_module, 'Task', None)
        if module is not None and callable(getattr(module, 'run', None)) and task is not None \
                and issubclass(task, CellTask):
            found.append(config)
    return found


def example_dir(config):
    return os.path.join(config.path, 'static', config.label, 'images')


def example_input(config):
    for path in sorted(glob.glob(os.path.join(example_dir(config), 'Example.*'))):
        if not path.endswith('.json'):
            return path
    return None


def example_info(config):
    """Description of an app's example for the API, or None."""
    path = example_input(config)
    if path is None:
        return None
    prefix = config.label + '/images/'
    info = {
        'app': config.label,
        'name': config.verbose_name,
        'version': sys.modules[config.name].version,
        'uploaded_image': static(prefix + os.path.basename(path)),
        'result_image': None,
        'result': None,
    }
    if os.path.isfile(os.path.join(example_dir(config), 'Example_r.jpg')):
        info['result_image'] = static(prefix + 'Example_r.jpg')
    result_path = os.path.join(example_dir(config), 'Example.json')
    if os.path.isfile(result_path):
        with open(result_path, encoding='utf-8') as fh:
            info['result'] = json.load(fh)
    return info
