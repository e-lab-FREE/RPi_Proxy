#!/bin/bash
sh ./start-video.sh > /dev/null 2>&1 &
sh ./start-hw-control.py > /dev/null 2>&1 &

