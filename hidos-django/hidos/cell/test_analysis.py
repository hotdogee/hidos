"""
The analysis algorithms must give the same numbers as the original
Python 2.7 / scikit-image 0.12 / OpenCV 3 stack (2016).

REFERENCE was produced by running the unmodified 2016 code on each app's
example image in a Python 2.7 container (tools/py2-baseline, see its README).

cellm1 reads JPEGs with skimage.io (Pillow). Pillow 3.3 decoded this JPEG
slightly differently from libjpeg-turbo (modern Pillow and OpenCV), so the
2016 number on the original pixels was 18.6998; fed the same (libjpeg-turbo)
pixels, the 2016 code gives 18.4340112555 -- the value checked here.
"""
import json
import os
import shutil
import sys

import pytest

from cell.examples import analysis_apps, example_input
from cell.management.commands.generate_examples import ExampleRecord
from cell.tasks import json_safe
from conftest import image_file

pytestmark = pytest.mark.analysis

REFERENCE = {
    'cella1': {"#Branch": 27, "#Extremity": 27, "#Junction": 110, "#Mesh": 79, "#Segment": 138,
               "Connectivity": 303, "Mean branch length": 58.867, "Mean mesh area": 8888.478,
               "Mean mesh perimeter": 339.316, "Mean segment length": 67.133, "Std. branch Length": 27.033,
               "Std. mesh area": 10115.852, "Std. mesh perimeter": 193.215, "Std. segment length": 59.061,
               "Tot. branch length": 1589, "Tot. mesh area": 702189, "Tot. mesh perimeter": 26805,
               "Tot. network length": 10853, "Tot. segment length": 9264},
    'cellc1': {"count": 111},
    'cellc2': {"confluence": "25.66"},
    'cellm1': {"ratio": 18.434011255490486},
    'cellm3': {"ratio": 21.91769547325103},
    'celln1': {"cell_body": 30, "dead_bodies": 4, "mean_branch": 144.133, "mean_length": 332.133,
               "mean_outgrowth": 4.8, "neurite_outgrowth": 144, "number_of_branches": 4324,
               "outgrowth_length": 9964},
}


@pytest.mark.parametrize('label', sorted(REFERENCE))
def test_algorithm_reproduces_2016_results(label, tmp_path):
    config = next(c for c in analysis_apps() if c.label == label)
    record = ExampleRecord(example_input(config), str(tmp_path))
    result = json_safe(sys.modules[config.name].run(record))
    expected = REFERENCE[label]
    assert set(result) == set(expected)
    for key, value in expected.items():
        if isinstance(value, float):
            assert result[key] == pytest.approx(value, rel=1e-9, abs=1e-9), key
        else:
            assert result[key] == value, key
    assert os.path.getsize(record.result_image.path) > 0
    assert os.path.getsize(record.result_display.path) > 0


def test_stored_example_results_are_current():
    """generate_examples output (Example.json) matches the current algorithms."""
    for config in analysis_apps():
        path = os.path.join(os.path.dirname(example_input(config)), 'Example.json')
        with open(path, encoding='utf-8') as fh:
            stored = json.load(fh)
        expected = REFERENCE[config.label]
        assert set(stored) == set(expected), config.label
        for key, value in expected.items():
            assert stored[key] == (pytest.approx(value) if isinstance(value, float) else value), (config.label, key)


@pytest.mark.django_db
def test_real_analysis_through_the_api(auth_client):
    """Upload the cellc2 example through the REST API and run the real algorithm (Celery eager)."""
    config = next(c for c in analysis_apps() if c.label == 'cellc2')
    with open(example_input(config), 'rb') as fh:
        upload = image_file()
        upload = type(upload)(fh.read())
    upload.name = 'example.jpg'
    response = auth_client.post('/api/v1/cell/c2/tasks', {'file': upload}, format='multipart')
    assert response.status_code == 201, response.content
    item = auth_client.get('/api/v1/fs/' + response.json()['id']).json()
    assert item['content']['status'] == 'success'
    assert item['content']['result'] == REFERENCE['cellc2']
    from cellc2.models import Task
    task = Task.objects.get(pk=response.json()['id'])
    assert os.path.getsize(task.result_display.path) > 0
    shutil.rmtree(os.path.dirname(task.uploaded_image.path))
