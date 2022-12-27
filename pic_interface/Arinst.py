import sys
import serial
import numpy as np
import json
import threading

from datetime import datetime



def act_generator(ser):
    
    ser.write(b'gon 0\r\n')
    #print('Estou vivo 1')
    #print(ser.in_waiting)
    #print(ser.out_waiting)
    ser.flush()
    ser.flush()
    return 
    
def set_sga(ser):
    ser.write(b'sga 10000 0\r\n')
    #print(ser.in_waiting)
    #print(ser.out_waiting)
    ser.flush()
    ser.flush()
    return 'gerador activo'

def scn22(ser, strat, stop, step):
    send = b'scn22 '+ str(strat).encode('ascii')  + b' ' + str(stop).encode('ascii')  + b' ' + str(step).encode('ascii')  + b' 200 20 10700000 10000 0\r\n'
    ser.write(send)
    #print(ser.in_waiting)
    #print(ser.out_waiting)
    return 

def get_data(ser):
    data_get = b''
    ser.readline()   # read a '\n' terminated line
    ser.readline()   # read a '\n' terminated line
    ser.readline()   # read a '\n' terminated line
    ser.readline()   # read a '\n' terminated line
    ser.readline()   # read a '\n' terminated line
    ser.readline()   # read a '\n' terminated line
    
    while (True):
        line7 = ser.readline()   # read a '\n' terminated line
        data_get+=line7
        #print(line7)
        if (line7 ==b'complete\r\n'):
                break
    # print('\n\r Final data: \n\r')
    # print(data_get)
    
    
    return data_get

def Test_Arinst(sererial_Spec,strat, stop, step, itera):
    freq = np.arange(strat, stop, step)
    for l in range(0,itera):
        act_generator(sererial_Spec)
        set_sga(sererial_Spec)
        scn22(sererial_Spec, strat, stop, step)
        data = get_data(sererial_Spec)
        spec= evalute_data_Final(data)
        # print(len(spec[1:]))
        # print(len(freq))
        # print(freq[0])
        # print(freq[-1])
        send_message = { "frequency": freq.tolist(), "magnitude": spec[1:]  }
        print(json.dumps(send_message, indent=4))
    return True

#data_final = arnist('COM3',3308000000, 3891000000, 500000, 4)

def evalute_data_Final(data):
    spec =[]
    index = len(data)-1
    # print(index)
    while (index>1):
        print(data[index])
        if (data[index] == 255):
            index -=1
            break
        index-=1
    # print(index)
    for i in range(0,index,2):
        #______________Versão de testes_________________________
        #val_1 = ((data_f[i] & 0b0111)<<8)
        #val_2 = (data_f[i+1] & 0x0FF)
        #print("val_1 ") 
        #print(val_1)
        #print("val_2 ")
        #print(val_2)
        #val_f = val_1 |val_2
        #_______________________________________________________.
        val = ((data[i] & 0b0111)<<8) | (data[i+1] & 0x0FF)
        # print((80*10.0-val)/10.0 ) # At 25dB to -25dB
        spec.append((80*10.0-val)/10.0)
    return spec