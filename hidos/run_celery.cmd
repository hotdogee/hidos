call ./hidos/env/Scripts/activate
cd hidos
celery -A hidos worker --loglevel=info
cd ..
call deactivate