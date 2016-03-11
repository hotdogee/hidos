#!/bin/bash -ve
. hidos/env/bin/activate
cd hidos
celery -A hidos worker --loglevel=info -n cellm.%h &
cd ..
deactivate
