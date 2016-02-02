#!/bin/bash -ve
sudo ps auxww | grep celery | grep -v "grep" | awk '{print $2}' | sudo xargs kill -9
sudo ps auxww | grep manage.py | grep -v "grep" | awk '{print $2}' | sudo xargs kill -9