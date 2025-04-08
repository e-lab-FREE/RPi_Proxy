import time
import GPIO as GPIO
import sys
import serial
import numpy as np
import json
import configparser

import threading

from datetime import datetime

OFF = GPIO.OFF
ON = GPIO.ON



if __name__ == "__main__":
    # arnist('/dev/ttyACM0', 3308000000, 3891000000, 500000, 4)
    status = GPIO.Int_GPIO()
    #print(status)
    #print(OFF)
    #print(ON)
    while True:
        input_msg = input()
        print(input_msg)
        if input_msg == 'm0':
            GPIO.Magnite_on_stat(OFF)
            GPIO.Magnite_1_stat(OFF)
            GPIO.Magnite_2_stat(OFF)
            break 
        elif input_msg == 'm1':
            GPIO.Magnite_1_stat(OFF)
            GPIO.Magnite_2_stat(OFF)
            GPIO.Magnite_on_stat(ON)
        elif input_msg == 'm2':
            GPIO.Magnite_1_stat(ON)
            GPIO.Magnite_2_stat(OFF)
            GPIO.Magnite_on_stat(ON)
            time.sleep(2)
        elif input_msg == 'm3':
            GPIO.Magnite_1_stat(OFF)
            GPIO.Magnite_2_stat(ON)
            GPIO.Magnite_on_stat(ON)
            time.sleep(2)        
        elif input_msg == 'm4':
            GPIO.Magnite_1_stat(ON)
            GPIO.Magnite_2_stat(ON)
            GPIO.Magnite_on_stat(ON)
            time.sleep(2)
        elif input_msg == 'ar':
            GPIO.Inject_Gas(3, 600)
        elif input_msg == 'he':
            GPIO.Inject_Gas(1, 600)
        elif input_msg == 'n':
            GPIO.Inject_Gas(2, 600)
        elif input_msg == 'ups':
            GPIO.Tomanda_energia_stat(ON)
        elif input_msg == 'pdis':
            GPIO.Power_Of_Discharge_stat(ON)
        elif input_msg == 'vacpump':
            GPIO.Vacum_Pump_stat(ON)
        elif input_msg == 'dis':
            GPIO.Discharge_stat(ON)
        elif input_msg == 'cut':
            GPIO.Valve_cut_off_stat(ON)
        else:
            pass




