#!/bin/bash -ve
cd hidos
virtualenv env
cd ..
. hidos/env/bin/activate
pip install -r hidos/requirements.txt
deactivate
