#!/bin/bash -ve
. hidos/env/bin/activate
cd hidos
celery -A hidos worker --loglevel=info -Q cellc1 -n cellc1.%h > ../../log/celeryout.log 2> ../../log/celeryerr.log &
cd ..
deactivate
