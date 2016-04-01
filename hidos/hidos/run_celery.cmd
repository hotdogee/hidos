call ./hidos/env/Scripts/activate
cd hidos
celery -A hidos worker --loglevel=info --concurrency=2 -Q app -n cellc.%h
cd ..
call deactivate