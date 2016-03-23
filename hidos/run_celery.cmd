call hidos\env\Scripts\activate
cd hidos
celery -A hidos worker --loglevel=info --concurrency=2 -Q cellc1 -n cellc1.%h
cd ..
call deactivate