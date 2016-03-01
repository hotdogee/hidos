#!/bin/bash -ve
ps auxww | grep celery | grep -v "grep" | awk '{print $2}' | xargs kill -9
ps auxww | grep manage.py | grep -v "grep" | awk '{print $2}' | xargs kill -9
