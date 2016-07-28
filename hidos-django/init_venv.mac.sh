#!/bin/bash -ve
cd hidos
virtualenv env
source ./env/bin/activate
pip install -r requirements.txt
# install opencv
ln -s /usr/local/Cellar/opencv/2.4.13/lib/python2.7/site-packages/cv2.so ./env/lib/python2.7/site-packages/cv2.so
source deactivate
cd ..
