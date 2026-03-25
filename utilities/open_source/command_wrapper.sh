#!/bin/bash

timeout=3600  # 1 hr timeout
cmd="$1"
args="$2"
file="$3"
stop_key="$4"

# Start the process in the background, redirecting stdin
# mkfifo cmdpipe
$cmd $args > /dev/null 2>&1 &
pid=$!

time_count=0
rm -f "$file"
while [ ! -f "$file" ]; do
    sleep 1
    time_count=$((time_count + 1))
    if [ $time_count -gt $timeout ]; then
        break
    fi
done

# Inject key to quit (usually 'q')
if [ "$stop_key" = "kill" ]; then
    kill -SIGINT $pid
else
    # echo "$stop_key" > cmdpipe
    echo "$stop_key"
fi

# Kill in 30s just in case graceful close didn't work
sleep 30
if kill -0 $pid 2>/dev/null; then
    kill -9 $pid
fi
