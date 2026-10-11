"""
The analysis algorithms must give the same numbers as the original
Python 2.7 / scikit-image 0.12 / OpenCV 3 stack (2016).

REFERENCE was produced by running the unmodified 2016 code on each app's
example image in a Python 2.7 container (tools/py2-baseline, see its README).

cellm1 reads JPEGs with skimage.io (Pillow). Pillow 3.3 decoded this JPEG
slightly differently from libjpeg-turbo (modern Pillow and OpenCV), so the
2016 number on the original pixels was 18.6998; fed the same (libjpeg-turbo)
pixels, the 2016 code gives 18.4340112555 -- the value checked here.

The example images are grey (R = G = B), so COLOUR_REFERENCE adds two colour
photos (cell/testdata: tools/data images downscaled with Pillow and saved as
PNG, which every OpenCV version decodes to the same pixels).
"""
import json
import math
import os
import shutil
import sys

import numpy as np
import pytest

from cell import skimage_compat as compat
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

TESTDATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testdata')

# The 2016 code gave these numbers with OpenBLAS's AVX-512, Haswell and
# Sandybridge kernels alike (OPENBLAS_CORETYPE, see tools/py2-baseline).
# Cell M1 on IMG_0159_640.png is left out: there the 2016 number
# (24.955312271564328) depends on the last bits of the resize matrix that
# scikit-image 0.12 got from an SVD; with the same matrix the port gives it
# too, with the exact matrix of compat.resize 24.955455043859647.
COLOUR_REFERENCE = {
    'IMG_0126_tungsten_800.png': {
        'cella1': {"#Branch": 16, "#Extremity": 17, "#Junction": 36, "#Mesh": 24, "#Segment": 47,
                   "Connectivity": 110, "Mean branch length": 83.594, "Mean mesh area": 8441.976,
                   "Mean mesh perimeter": 332.096, "Mean segment length": 74.053, "Std. branch Length": 50.188,
                   "Std. mesh area": 10901.616, "Std. mesh perimeter": 183.185, "Std. segment length": 65.107,
                   "Tot. branch length": 1337, "Tot. mesh area": 202607, "Tot. mesh perimeter": 7970,
                   "Tot. network length": 4817, "Tot. segment length": 3480},
        'cellc1': {"count": 1947},
        'cellc2': {"confluence": "46.17"},
        'cellm1': {"ratio": 98.97496682833089},
        'cellm3': {"ratio": 0.0},
        'celln1': {"cell_body": 22, "dead_bodies": 4, "mean_branch": 318.045, "mean_length": 366.864,
                   "mean_outgrowth": 5.318, "neurite_outgrowth": 117, "number_of_branches": 6997,
                   "outgrowth_length": 8071},
    },
    'IMG_0159_640.png': {
        'cella1': {"#Branch": 26, "#Extremity": 26, "#Junction": 38, "#Mesh": 25, "#Segment": 44,
                   "Connectivity": 114, "Mean branch length": 50.697, "Mean mesh area": 3627.828,
                   "Mean mesh perimeter": 220.45, "Mean segment length": 58.381, "Std. branch Length": 28.445,
                   "Std. mesh area": 5399.25, "Std. mesh perimeter": 183.974, "Std. segment length": 49.159,
                   "Tot. branch length": 1318, "Tot. mesh area": 90695, "Tot. mesh perimeter": 5511,
                   "Tot. network length": 3886, "Tot. segment length": 2568},
        'cellc1': {"count": 1270},
        'cellc2': {"confluence": "48.19"},
        'cellm3': {"ratio": 30.80357142857143},
        'celln1': {"cell_body": 23, "dead_bodies": 44, "mean_branch": 50.739, "mean_length": 54.0,
                   "mean_outgrowth": 1.304, "neurite_outgrowth": 30, "number_of_branches": 1167,
                   "outgrowth_length": 1242},
    },
}


def run_and_check(label, image, expected, tmp_path):
    config = next(c for c in analysis_apps() if c.label == label)
    record = ExampleRecord(image, str(tmp_path))
    result = json_safe(sys.modules[config.name].run(record))
    assert set(result) == set(expected)
    for key, value in expected.items():
        if isinstance(value, float):
            assert result[key] == pytest.approx(value, rel=1e-9, abs=1e-9), key
        else:
            assert result[key] == value, key
    assert os.path.getsize(record.result_image.path) > 0
    assert os.path.getsize(record.result_display.path) > 0


@pytest.mark.parametrize('label', sorted(REFERENCE))
def test_algorithm_reproduces_2016_results(label, tmp_path):
    config = next(c for c in analysis_apps() if c.label == label)
    run_and_check(label, example_input(config), REFERENCE[label], tmp_path)


@pytest.mark.parametrize('image,label', [(image, label) for image in sorted(COLOUR_REFERENCE)
                                         for label in sorted(COLOUR_REFERENCE[image])])
def test_algorithm_reproduces_2016_results_on_colour_images(image, label, tmp_path):
    run_and_check(label, os.path.join(TESTDATA, image), COLOUR_REFERENCE[image][label], tmp_path)


def test_bgr2gray_is_the_opencv3_conversion():
    """OpenCV 3.4 values; OpenCV 4 gives one grey level more or less for these (and 43858 other) colours."""
    bgr = [(250, 0, 0), (180, 37, 41), (116, 11, 83), (30, 238, 125), (18, 68, 169), (130, 193, 212)]
    image = np.array([bgr], dtype=np.uint8)
    assert compat.bgr2gray(image).tolist() == [[29, 55, 45, 180, 92, 191]]


def test_py2_round():
    assert compat.py2_round(77 / 16, 3) == 4.813  # Python 3: 4.812
    assert compat.py2_round(-77 / 16, 3) == -4.813
    assert compat.py2_round(0.125, 2) == 0.13
    assert compat.py2_round(2.675, 2) == 2.67  # 2.67499999999999982236431605997495353221893310546875
    assert compat.py2_round(1250, -2) == 1300.0
    assert compat.py2_round(2.5) == 3.0 and compat.py2_round(-0.5) == -1.0
    assert math.isnan(compat.py2_round(float('nan'), 3))


def test_canny_smoothing_kernel_is_platform_independent():
    """The sigma=2 Gaussian weights of scipy 0.17 (2016), bit for bit."""
    expected = ['0x1.18aad19e4159bp-14', '0x1.c98b8c5d0dda5p-12', '0x1.227362b5fc92dp-9', '0x1.1f30504e20207p-7',
                '0x1.ba4d4125ffd2ap-6', '0x1.0941b71ceef37p-4', '0x1.ef9093fc46e5ap-4', '0x1.68856f9ab1983p-3',
                '0x1.98862a07ae7b4p-3']
    weights = [float(w).hex() for w in compat._gaussian_kernel(2)]
    assert weights == expected + expected[-2::-1]


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
