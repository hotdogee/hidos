call ./hidos/env/Scripts/activate
cd hidos
del db.sqlite3
rd /s /q media\image_analysis\task
python manage.py migrate
python manage.py loaddata ../users.json
cd ..
call deactivate
