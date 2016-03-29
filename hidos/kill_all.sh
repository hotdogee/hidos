#!/bin/bash -ve
ps auxww | grep celery | grep -e "/cellm2/" | grep -v "grep" | awk '{print $2}' | xargs kill -9
ps auxww | grep manage.py | grep -e "8003" | grep -v "grep" | awk '{print $2}' | xargs kill -9
