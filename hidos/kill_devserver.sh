#!/bin/bash -ve
ps auxww | grep manage.py | grep -e "8003" | grep -v "grep" | awk '{print $2}' | xargs kill -9
