cd hidos
virtualenv env
call .\env\Scripts\activate
pip install -r dev-requirements.txt
call deactivate
cd ..
