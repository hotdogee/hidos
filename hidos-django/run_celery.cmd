call ./hidos/env/Scripts/activate
cd hidos
rem Use CTRL+BREAK to interrupt the application.
start /w /b celery -A hidos worker --loglevel=info --concurrency=2 -Q cell -n cell.%h
cd ..
call deactivate
