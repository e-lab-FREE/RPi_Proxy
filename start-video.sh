#!/bin/bash
pendulum_location=Lisbon
pendulum_name="pendulo 12"
video_server=127.0.0.1
video_port=10000
usb_camera=/dev/video2
video_width=800
video_height=600
#video_frame=30/1
video_frame=30

killall ffmpeg
ffmpeg -s $video_width\x$video_height -f video4linux2 -i $usb_camera -r $video_frame \
       -vf "drawtext = fontfile = /usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf: text ='$pendulum_location ($pendulum_name) - %{localtime\:%X}': :fontsize=20:fontcolor=black:box=1:boxcolor=white@0.5: x = 10: y = 10 " \
       -pix_fmt yuv420p -an -c:v libx264 -profile:v baseline  -tune zerolatency -flags global_header -bsf dump_extra \
       -f rtp "rtp://$video_server:$video_port/?pkt_size=1000"
