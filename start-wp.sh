#!/bin/bash
video_server=elab1.ist.utl.pt
video_port=8006
usb_camera=/dev/video0
video_width=1280
video_height=720
video_frame=30/1

killall python3
killall gst-launch-1.0
python3 main.py > /dev/null 2>&1 &
gst-launch-1.0 v4l2src device=$usb_camera ! video/x-raw,width=$video_width,height=$video_height,framerate=$video_frame ! clockoverlay time-format="%x - %X" ! videoconvert ! omxh264enc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=$video_server port=$video_port async=false > /dev/null 2>&1 &
