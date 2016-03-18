call ./hidos/env/Scripts/activate
cd hidos
celery -A hidos worker --loglevel=info --concurrency=2 -Q cellm -n cellm.%h
cd ..
call deactivate