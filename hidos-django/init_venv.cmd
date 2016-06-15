cd hidos
virtualenv env
call .\env\Scripts\activate
pip install -r requirements.txt
rem install opencv
copy ..\cv\win64\cv2.pyd .\env\Lib\site-packages\cv2.pyd
call deactivate
cd ..
