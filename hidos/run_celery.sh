#!/bin/bash -ve
. hidos/env/bin/activate
cd hidos
celery -A hidos worker --loglevel=info -n cellm.%h > ../celeryout.log 2> ../celeryerr.log &
cd ..
deactivate
