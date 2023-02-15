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
        if input_msg == '0':
            GPIO.Magnite_on_stat(OFF)
            GPIO.Vacum_Pump_stat(OFF)
            time.sleep(2)
            GPIO.Magnite_1_stat(OFF)
            GPIO.Magnite_2_stat(OFF)
            break 
        elif input_msg == '1':
            GPIO.Magnite_1_stat(OFF)
            GPIO.Magnite_2_stat(OFF)
            GPIO.Vacum_Pump_stat(ON)
            time.sleep(0.1)
            GPIO.Magnite_on_stat(ON)
        elif input_msg == '2':
            GPIO.Magnite_1_stat(ON)
            GPIO.Magnite_2_stat(OFF)
            time.sleep(0.1)
            GPIO.Magnite_on_stat(ON)
            time.sleep(2)
        elif input_msg == '3':
            GPIO.Magnite_1_stat(OFF)
            GPIO.Magnite_2_stat(ON)
            time.sleep(0.1)
            GPIO.Magnite_on_stat(ON)
            time.sleep(2)        
        elif input_msg == '4':
            GPIO.Magnite_1_stat(ON)
            GPIO.Magnite_2_stat(ON)
            time.sleep(0.1)
            GPIO.Magnite_on_stat(ON)
            time.sleep(2)
        elif input_msg == 'OpAr':
            GPIO.Valve_cut_off_stat(ON)
            GPIO.Vacum_Pump_stat(ON)
            GPIO.Inject_Gas(3, 14)
        elif input_msg == 'on':
            GPIO.Vacum_Pump_stat(ON)
            GPIO.Discharge_stat(ON)
        elif input_msg =='off':
            GPIO.Discharge_stat(OFF)
        elif input_msg == 'vac':
            GPIO.Valve_cut_off_stat(ON)
        elif input_msg == 'vacf':
            GPIO.Valve_cut_off_stat(OFF)

        else:
            pass




