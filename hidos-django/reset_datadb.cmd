call ./hidos/env/Scripts/activate
cd hidos
del db.sqlite3
del /s /q media\cell*
rd /s /q media\cellc2
python manage.py migrate
python manage.py loaddata ../users.json
cd ..
call deactivate
