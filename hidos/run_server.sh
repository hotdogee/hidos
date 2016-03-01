#!/bin/bash -ve
. hidos/env/bin/activate
python ./hidos/manage.py runserver 0.0.0.0:8001 &
deactivate
