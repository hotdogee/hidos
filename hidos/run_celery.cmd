call hidos\env\Scripts\activate
cd hidos
celery -A hidos worker --loglevel=info --concurrency=2 -Q cellq -n cellq.%h
cd ..
call deactivate