from ctypes import ArgumentError
import RPi.GPIO as GPIO
import time
import sys
import serial
import numpy as np
import json
import configparser

import threading

from datetime import datetime


# sys.path.append('/home/pi/Cavidade/elab/webgpio/modules')
import pic_interface.PPT200 as PPT200
import pic_interface.Arinst as Arinst
import pic_interface.GPIO as GPIO
import pic_interface.Send_data as send_data

presure = None
ON = 1
OFF = 0
next_execution = None
config_send = None
exp_run = None
SAVE_DATA = []

def Mauser_pressure(COMfree,serial_pressure):
    global pressure
    global exp_run
    global SAVE_DATA
    while exp_run:
        pressure = "{:.3f}".format(PPT200.get_pressure(serial_pressure))
        send_message = {"time":str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]),"pressure": pressure}
        print(json.dumps(send_message, indent=4))
        time.sleep(0.001)
        SAVE_DATA.append(send_message)
        send_message = {"execution": next_execution,"value":send_message,"result_type":"p"}#,"status":"running"}
        # send_data.SendPartialResult(conn,send_message,config_send,HEADERS)
        COMfree.SendResult(send_message)
    return



def Set_Up_Exp(pressure_ref,gas_select,gas_amount):
    global pressure
    max_time = 2000
    numero = 0 
    ligar = 1
    GPIO.Vacum_Pump_stat(ON)
    time.sleep(5)
    while (float(pressure)>float(pressure_ref)):
        print("aqui: ",pressure)
        print("aqui: ",pressure_ref)
        print(float(pressure)>float(pressure_ref))
        numero = numero +1
        if (ligar == 1):
            GPIO.Valve_cut_off_stat(ON)
            ligar = 0
        time.sleep(1)
        if numero >max_time:
            break        
    time.sleep(5)
    # wait untly pressure is less them press_back
    GPIO.Valve_cut_off_stat(OFF)
    GPIO.Inject_Gas(int(gas_select), gas_amount)
    return

def Do_analise_Spec(COMfree,serial_arinst,strat, stop, step, itera):
    global pressure
    global SAVE_DATA
    global exp_run
    freq = np.arange(strat, stop, step)
    for l in range(0,itera):
        Arinst.act_generator(serial_arinst)
        Arinst.set_sga(serial_arinst)
        Arinst.scn22(serial_arinst, strat, stop, step)
        data = Arinst.get_data(serial_arinst)
        spec= Arinst.evalute_data_Final(data)
        # print(len(spec[1:]))
        # print(len(freq))
        # print(freq[0])
        # print(freq[-1])
        send_message = {"time":str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]),"pressure": pressure,"frequency": freq.tolist(), "magnitude": spec[1:]}
        print(json.dumps(send_message, indent=4))
        SAVE_DATA.append(send_message)
        send_message = {"execution": next_execution,"value":send_message,"result_type":"p"}#,"status":"running"}
        # COMfree
        # send_data.SendPartialResult(conn,send_message)
        COMfree.SendResult(send_message)
    return
    


def Do_experiment(COMfree,id_exe,serial_pressure, serial_arinst,strat, stop, step, itera,back_ground,gas_pressure,gas_type,Discharge,Magnite_field):
    global next_execution
    global exp_run
    global SAVE_DATA
    SAVE_DATA =[]
    next_execution = id_exe
    print("F_start: ", strat)
    print("F_end: ", stop)
    print("F_step: ", step)
    print("n_iteration: ", itera)
    print("back_pressure: ",back_ground)
    print("pressure: ",gas_pressure )
    print("gas_selector: ", gas_type)
    exp_run =True
    data_thread = threading.Thread(target=Mauser_pressure,args=(COMfree,serial_pressure,),daemon=True)
    # arnist('/dev/ttyACM0', 3308000000, 3891000000, 500000, 4)
    data_thread.start()
    # Set Up experiment:
    
    Set_Up_Exp(back_ground,gas_type,gas_pressure)
    time.sleep(2)
    if (Discharge == 1):
        GPIO.Discharge_stat(ON)
    time.sleep(2)
    if (Magnite_field == 1):    
        GPIO.Magnite_on_stat(ON)
        time.sleep(5)
    elif (Magnite_field == 2):
        GPIO.Magnite_1_stat(ON)
        time.sleep(0.1)
        GPIO.Magnite_on_stat(ON)
        time.sleep(2)
    elif (Magnite_field == 3):
        GPIO.Magnite_2_stat(ON)
        time.sleep(0.1)
        GPIO.Magnite_on_stat(ON)
        time.sleep(2)
    elif (Magnite_field == 4):
        GPIO.Magnite_1_stat(ON)
        GPIO.Magnite_2_stat(ON)
        time.sleep(0.1)
        GPIO.Magnite_on_stat(ON)
        time.sleep(2)
    Do_analise_Spec(COMfree,serial_arinst, strat, stop, step, itera)
    time.sleep(5)
    if (Discharge == 1):
        GPIO.Discharge_stat(OFF)
    if (Magnite_field >= 1):    
        GPIO.Magnite_on_stat(OFF)
        time.sleep(2)
        GPIO.Magnite_1_stat(OFF)
        GPIO.Magnite_2_stat(OFF)
    GPIO.Vacum_Pump_stat(OFF)
    exp_run =False
    send_message = {"execution":next_execution,"value":SAVE_DATA,"result_type":"f"}
    # send_data.SendPartialResult(conn,send_message,config_send,HEADERS)
    COMfree.SendResult(send_message)
    SAVE_DATA = []
    return True
