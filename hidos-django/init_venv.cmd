cd hidos
virtualenv env
cd ..
call .\hidos\env\Scripts\activate
pip install -r hidos\requirements.txt
call deactivate
