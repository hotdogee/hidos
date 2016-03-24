call ./hidos/env/Scripts/activate
cd hidos
celery -A hidos worker --loglevel=info --concurrency=2 -Q app -n cellc2.%h
cd ..
call deactivate