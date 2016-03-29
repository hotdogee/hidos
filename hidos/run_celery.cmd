call hidos\env\Scripts\activate
cd hidos
celery -A hidos worker --loglevel=info --concurrency=2 -Q cellm2 -n cellm2.%h
cd ..
call deactivate