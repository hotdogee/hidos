#!/bin/bash -ve
ps auxww | grep manage.py | grep -e "8000" | grep -v "grep" | awk '{print $2}' | xargs kill -9
