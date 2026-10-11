call ./hidos/env/Scripts/activate
cd hidos
rem Use CTRL+BREAK to interrupt the application.
rem The prefork pool is not supported on Windows, use the solo pool
start /w /b celery -A hidos worker --loglevel=info --pool=solo -Q cell -n cell.%h
cd ..
call deactivate
