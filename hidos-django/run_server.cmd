call ./hidos/env/Scripts/activate
cd hidos
start /w /b python manage.py runserver
cd ..
call deactivate