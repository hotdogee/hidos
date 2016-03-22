call ./hidos/env/Scripts/activate
cd hidos
python manage.py dumpdata auth.user --indent=4 > ../users.json
cd ..
call deactivate