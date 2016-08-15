dropdb -U postgres django
createdb -U postgres --owner django django hidos-django
call ./hidos/env/Scripts/activate
cd hidos
del /s /q media\cell*
rd /s /q media\cellc2
python manage.py migrate
rem python manage.py dumpdata users.user --indent 2
python manage.py loaddata ../users.json
cd ..
call deactivate
