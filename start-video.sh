#!/bin/bash
video_server=elab1.ist.utl.pt
video_port=6001
usb_camera=/dev/video100
video_width=640
video_height=480
video_frame=10/1

killall gst-launch-1.0
gst-launch-1.0 v4l2src device=$usb_camera ! video/x-raw,width=$video_width,height=$video_height,framerate=$video_frame ! clockoverlay time-format="%x - %X" ! videoconvert ! omxh264enc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=$video_server port=$video_port async=false 
