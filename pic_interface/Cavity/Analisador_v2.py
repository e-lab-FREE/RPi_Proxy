import sys
import serial
import numpy as np
import json
import pandas as pd
import configparser

from datetime import datetime


# sys.path.append('/home/pi/Cavidade/elab/webgpio/modules')
import PPT200 as PPT200


def int_com(COM):
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = COM
    ser.timeout = 200
    ser.open()
    print(COM)
    return  ser

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
    print('\n\r Final data: \n\r')
    print(data_get)
    
    
    return data_get


def init_saver(strat, stop, step,itera):
    size = ((stop-strat)/step)
    columns = ['Frequency [Hz]','Amp_0[dB] \n(P = ']
    save=np.zeros([int(size)+1, itera+1])
    print (size)
    data = ["" for i in range(itera)]
    
    if (itera >1):
        for i in range(1,itera):
            tag='Amp_'+str(i)+'[dB] \n(P = '
            columns.append(tag)
            
    return columns, save, data

def evalute_data(data, strat, stop, step, itera, save):
    f=strat
    for k in range(0,itera):
        t=0
        index = len(data[k])-1
        print(index)
        while (index>1):
            print(data[k][index])
            if (data[k][index] == 255):
                index -=1
                break
            index-=1
        print(index)
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
            val = ((data[k][i] & 0b0111)<<8) | (data[k][i+1] & 0x0FF)
            if (k==0):
                save[t][0]=f
                f=f+step
            save[t][k+1]=(80*10.0-val)/10.0  # At 25dB to -25dB
            print (save[t][k+1])
            t=t+1
    return save

def close_port(ser):
    ser.close()
    return'closed'


 

def csv_filename():
    now = datetime.now() # current date and time
    filename = now.strftime("arinst_%Y-%m-%d_%H%M%S.csv")
    print("filename :", filename)
    return filename


def upload_path():
    path = '';

    try:
        config = configparser.RawConfigParser()
        config.read('config.cfg')
        upload_dict = dict(config.items('upload'))
        path = upload_dict['path']
    except:
        print('Check config.cfg !!!')
        pass

    return path


def filename():
    return upload_path() + csv_filename()


def arnist(COM,strat, stop, step, itera):
    ser = int_com(COM)
    columns,save,data = init_saver(strat, stop, step,itera)
    #print('Estou vivo')
    #act_generator(ser)
    #set_sga(ser)
    serial_pressure = PPT200.int_com_PPT200('/dev/ttyUSB0')
    for l in range(0,itera):
        #print('Estou vivo dentro 0')
        #pressure = PPT200.get_pressure(serial_pressure)
        columns[l+1]=columns[l+1]+"{:.3f}".format(PPT200.get_pressure(serial_pressure))+ ' [mbar])'
        act_generator(ser)
        set_sga(ser)
        scn22(ser, strat, stop, step)
        #print('Estou vivo 1')
        data[l] = get_data(ser)
        #print('Estou vivo 2')
    serial_pressure.close();
    save = evalute_data(data, strat, stop, step, itera, save)
    #print('Estou vivo 3')

    df = pd.DataFrame(save, columns = columns)
    result = df.to_json(orient="records")
    parsed = json.loads(result)
    
    # print('filename : {} '.format(filename()))

    df.to_csv(filename(), index=False)
    # json.dumps(parsed, indent=4) 
    #print('Estou vivo 4')
    
    close_port(ser)
    
    return parsed
    
    
#data_final = arnist('COM3',3308000000, 3891000000, 500000, 4)



if __name__ == "__main__":
    arnist('/dev/ttyACM0', 3308000000, 3891000000, 500000, 4)
