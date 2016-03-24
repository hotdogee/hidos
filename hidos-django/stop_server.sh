#!/bin/bash -ve
ps auxww | grep manage | grep -v "grep" | awk '{print $2}' | sudo xargs kill -9