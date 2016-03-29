#!/bin/bash -ve
. hidos/env/bin/activate
cd hidos
rm -f db.sqlite3
rm -rf media/cellm2/task/*
python manage.py migrate
python manage.py loaddata ../users.json
cd ..
deactivate