#!/bin/bash -ve
. hidos/env/bin/activate
cd hidos
rm -f db.sqlite3
rm -rf media/cellq/task/*
python manage.py migrate
python manage.py loaddata ../users.json
cd ..
deactivate