#!/bin/bash -ve
. hidos/env/bin/activate
python ./hidos/manage.py migrate
deactivate
