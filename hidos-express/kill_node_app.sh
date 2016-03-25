ps auxww | grep "node app" | grep -v "grep" | awk '{print $2}' | xargs kill -9

