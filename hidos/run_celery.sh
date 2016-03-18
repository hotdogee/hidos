#!/bin/bash -ve
. hidos/env/bin/activate
cd hidos
celery -A hidos worker --loglevel=info > ../../log/celeryout.log 2> ../../log/celeryerr.log  &
cd ..
deactivate
