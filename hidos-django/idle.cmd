call ./hidos/env/Scripts/activate
cd hidos
python -c "from idlelib.PyShell import main; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','hidos.settings.local'); import django; django.setup(); main()"
cd ..
call deactivate
rem from fs.serializers import FileSerializer