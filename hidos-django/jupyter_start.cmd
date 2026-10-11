rem Start Jupyter Notebook server
cd hidos
if not exist env py -3 -m venv env
call .\env\Scripts\activate
jupyter nbextension enable --py --sys-prefix widgetsnbextension
start /w /b jupyter notebook
call deactivate
cd ..
