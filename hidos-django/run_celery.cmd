call ./hidos/env/Scripts/activate
cd hidos
celery -A hidos worker --loglevel=info --concurrency=2 -Q cell -n cell.%h
cd ..
call deactivate
