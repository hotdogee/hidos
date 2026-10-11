rem Python 3.12+ virtualenv in hidos\env (numpy, scipy and OpenCV come as wheels)
cd hidos
py -3 -m venv env
call .\env\Scripts\activate
python -m pip install -U pip
pip install -r requirements\local.txt
call deactivate
cd ..
