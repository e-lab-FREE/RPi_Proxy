#!/bin/bash
video_server=elab1.ist.utl.pt
video_port=8005
usb_camera=/dev/video15

killall python3
killall gst-launch-1.0
python3 main.py > /dev/null 2>&1 &
gst-launch-1.0 v4l2src device=$usb_camera ! video/x-raw,width=640,height=480,framerate=10/1 ! clockoverlay time-format=\"%x - %X\" ! videoconvert ! x264enc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=$video_server port=$video_port async=false > /dev/null 2>&1 &
