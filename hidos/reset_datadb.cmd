call ./hidos/env/Scripts/activate
cd hidos
del db.sqlite3
rd /s /q media\cellm2\task
python manage.py migrate
python manage.py loaddata ../users.json
cd ..
call deactivate