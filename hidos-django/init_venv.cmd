cd hidos
virtualenv env
call .\env\Scripts\activate
pip install ..\lib\win64\numpy-1.11.1+mkl-cp27-cp27m-win_amd64.whl
pip install ..\lib\win64\scipy-0.17.1-cp27-cp27m-win_amd64.whl
pip install -r requirements.txt
rem install opencv
copy ..\lib\win64\cv2.pyd .\env\Lib\site-packages\cv2.pyd
call deactivate
cd ..
