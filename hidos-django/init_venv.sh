#!/bin/bash -ve
# Python 3.12+ virtualenv in hidos/env (numpy, scipy and OpenCV come as wheels)
cd hidos
python3 -m venv env
. ./env/bin/activate
python -m pip install -U pip
pip install -r requirements/local.txt
deactivate
cd ..
