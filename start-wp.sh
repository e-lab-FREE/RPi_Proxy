#!/bin/bash

sh ./video-stream.sh > /dev/null 2>&1 &

killall python3
python3 main.py > /dev/null 2>&1 &
