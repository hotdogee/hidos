#!/bin/bash -ve
. hidos/env/bin/activate
cd hidos
python manage.py runserver 0.0.0.0:8001 > ../../log/runserverout.log 2> ../../log/runservererr.log &
cd ..
deactivate
