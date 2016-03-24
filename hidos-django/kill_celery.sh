#!/bin/bash -ve
ps auxww | grep celery | grep -e "/app/" | grep -v "grep" | awk '{print $2}' | xargs kill -9
