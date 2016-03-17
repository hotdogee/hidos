#!/bin/bash -ve
. hidos/env/bin/activate
cd hidos
python manage.py runserver 0.0.0.0:8001 &
cd ..
deactivate
