rem Start Jupyter Notebook server
cd hidos
virtualenv env
call .\env\Scripts\activate
jupyter nbextension enable --py --sys-prefix widgetsnbextension
start /w /b jupyter notebook
call deactivate
cd ..
