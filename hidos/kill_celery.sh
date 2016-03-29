#!/bin/bash -ve
ps auxww | grep celery | grep -e "/cellm2/" | grep -v "grep" | awk '{print $2}' | xargs kill -9
