call ./hidos/env/Scripts/activate
cd hidos
rem Use CTRL+BREAK to interrupt the application.
start /w /b python manage.py runserver 8000
cd ..
call deactivate