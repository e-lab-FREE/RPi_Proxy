# RPi Proxy
This is a simple proxy that communicate with the main server. 

## Requirements

Install the following:
```
sudo  apt-get install git
```

For the video stream:
```
sudo apt-get install gstreamer1.0-tools
```
```
sudo apt-get install gstreamer1.0-plugins-good
```
```
sudo apt-get install gstreamer1.0-plugins-bad
```
```
sudo apt-get install gstreamer1.0-plugins-ugly
```
```
sudo apt-get install gstreamer1.0-plugins-base
```
For the Proxy it self:
```
sudo apt install python3
```
```
sudo apt install python3-pip
```
```
pip3 install pyserial
```

## How to connect to [FREE_Web](https://github.com/e-lab-FREE/FREE_Web)
To be able to comunicate with your main server, you need to change the configuration of the proxy you need to edit the following file:

* `server_info.ini` - change the SERVER, PORT with the corresponding to your server and the APPARATUS ID, EXPERIMENT_ID, SECRET corresponding to the information on the database of your main server ([FREE_Web](https://github.com/e-lab-FREE/FREE_Web))

```ini
[DEFAULT]
SERVER = elab1.ist.utl.pt
PORT = 5000
APPARATUS_ID = 1
EXPERIMENT_ID = 1
SECRET = test_1
```

*  `strat-video.sh` - change the video_server and video_port with the info of your video server (with janus installed). Also change the following parameters: usb_camera, video_width, video_height, video_height and video_frame, with the ones that your camara.


```sh
#!/bin/bash
video_server=elab1.ist.utl.pt
video_port=8006
usb_camera=/dev/video0
video_width=1280
video_height=720
video_frame=30/1

killall gst-launch-1.0
gst-launch-1.0 v4l2src device=$usb_camera ! video/x-raw,width=$video_width,height=$video_height,framerate=$video_frame ! clockoverlay time-format="%x - %X" ! videoconvert ! omxh264enc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=$video_server port=$video_port async=false 
```
Some usefull comands:
```
v4l2-ctl --list-devices
```
```
v4l2-ctl -d /dev/video2 --list-formats-ext
```


## About


This RPi Proxy it was devoloped to the project World Pendulum, and for it the interface.py was developed to operate a pendulum controled with a dsPIC. 
But anyone can change the interface.py and this proxy can do all kandies of experiment the only this is requested to the user to be careful is to not modify the name of the following function:  

```python3
# Reads the data sent by the controller after an experiment was initiated
 def  receive_data_from_exp():
     ...
     return results # JSON
     
 #  Where the config json will be a JSON that was the information of the controlor of 
 # the experiment so the RPi can communicate to it
 def do_init(config_json): 
     ...
     return True/False 
    
 # The config_json is the configuration given by the user that he/she wants to execute 
 def do_config(config_json) :
     ...
     return True/False
 
 # Strats the experiment 
 def do_start() :
     ...
     return True/False 

 # Stops the experiment
 def do_stop() :
      ...
     return True/False
     
 # Rests the experiment    
 def do_reset() :
      ...
     return True/False
 
 # Gets the information about the experiment (sensors)
 def get_status():
      ...
     return status
```
