#!/bin/bash -ve
cd hidos
virtualenv env
./env/bin/activate
pip install -r requirements/local.txt
# install opencv
ln -s /usr/local/lib/python2.7/site-packages/cv2.so ./env/lib/python2.7/site-packages/cv2.so
deactivate
cd ..