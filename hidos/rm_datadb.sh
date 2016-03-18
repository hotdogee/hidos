#!/bin/bash -ve
. hidos/env/bin/activate
cd hidos
rm -f db.sqlite3
rm -rf media/image_analysis/task/*
cd ..
deactivate
