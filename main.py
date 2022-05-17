import configparser
import importlib
import json
import os
import re
import requests
import serial
import sys
import threading
import time
from datetime import datetime


lock = threading.Lock()

config_info = configparser.ConfigParser(interpolation=None)
SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))
config_file = os.path.join(SCRIPT_DIR, 'server_info.ini')
if not os.path.isfile(config_file):
    print("*ERROR: config file not found!\n\tRequired file is {}".format(config_file))
    sys.exit(1)
try:
    config_info.read(config_file)
except:
    print("*ERROR: parsing ini file failed!")
    sys.exit(1)

FORMAT = 'utf-8'

CONFIG_OF_EXP = []
next_execution = {}
status_config= {}
SAVE_DATA = []

test =False
test_end_point_print = True
Working = False
Waiting_for_config = True

interface = None

HEADERS = {
  "Authentication": str(config_info['DEFAULT']['SECRET']),
  "Content-Type": "application/json"
}

def SendInfoAboutExecution(id):
    global CONFIG_OF_EXP
    api_url = BASE_API_URL + "execution/" + str(id) + "/status"
    # msg = {"secret":SEGREDO}
    print(api_url)
    response =  requests.patch(api_url, headers =HEADERS,json={"status": "R"})
    print(response)
    return ''

def send_exp_data():
    global SAVE_DATA
    global Working
    global next_execution
    global lock
    while interface.receive_data_from_exp() != "DATA_START":
        pass
    # send_message = {"value":"","result_type":"p"}#,"status":"Experiment Starting"}
    # SendPartialResult(send_message)
    while True:
        exp_data = interface.receive_data_from_exp()
        if config_info['DEFAULT']['DEBUG'] == "on":
            print("What pic send on serial port (converted to json): ",json.dumps(exp_data,indent=4))
        try:
            exp_data = json.loads(exp_data)
        except:
            pass
        if exp_data != "DATA_END":

            SAVE_DATA.append(exp_data)
            send_message = {"execution":int(next_execution["id"]),"value":exp_data,"result_type":"p"}#,"status":"running"}
            SendPartialResult(send_message)
        else:
            send_message = {"execution":int(next_execution["id"]),"value":SAVE_DATA,"result_type":"f"}
            SendPartialResult(send_message)
            Working = False
            next_execution = {}
            SAVE_DATA=[]
            time.sleep(0.00001)
            return


def Send_Config_to_Pic(myjson):
    global Working
    global Waiting_for_config
    print("Recebi mensagem de configurestart. A tentar configurar pic")
    actual_config, config_feita_correcta = interface.do_config(myjson)
    if config_feita_correcta :   #se config feita igual a pedida? (opcional?)
        print(myjson["id"])
        SendInfoAboutExecution(myjson["id"])
        data_thread = threading.Thread(target=send_exp_data,daemon=True)
        print("PIC configurado.\n")
        if interface.do_start():                            #tentar começar experiencia
            Working = True
            data_thread.start()
            time.sleep(0.000001)
            #O JSON dos config parameters está mal e crasha o server. ARRANJAR
            #send_mensage = '{"reply_id": "2","status":"Experiment Running","config_params":"'+str(myjson["config_params"])+'}'
            # Working = True
            send_mensage = {"reply_id": "2","status":"Experiment Running"}
        else :
            send_mensage = {"reply_id": "2", "error":"-1", "status":"Experiment could not start"}

    else:
        send_mensage = {"reply_id": "2", "error":"-2", "status":"Experiment could not be configured"}
    return send_mensage



# REST
def GetConfig():
    global CONFIG_OF_EXP
    api_url = BASE_API_URL + "apparatus/" + config_info['DEFAULT']['APPARATUS_ID']
    # msg = {"secret":SEGREDO}
    print(api_url)
    response =  requests.get(api_url, headers =HEADERS)
    # print(response.json())
    print(response.json())
    CONFIG_OF_EXP = response.json()
    if config_info['DEFAULT']['DEBUG'] == "on":
        print(json.dumps(CONFIG_OF_EXP,indent=4))
    return ''

def GetExecution():
    global next_execution
    api_url = BASE_API_URL + "apparatus/" + config_info['DEFAULT']['APPARATUS_ID'] + "/nextexecution"
    response =  requests.get(api_url,headers = HEADERS)
    if (response.json()['protocol']['config'] !=None):
        print(response.json())
        next_execution = response.json()
    if config_info['DEFAULT']['DEBUG'] == "on":
        print("REQUEST\n")
        print(json.dumps(next_execution,indent=4))
    return ''


def SendPartialResult(msg):
    global next_execution
    # print(next_execution)

    api_url = BASE_API_URL + "result"
    if config_info['DEFAULT']['DEBUG'] == "on":
        print(str(msg))
        print(api_url)
        print("Aqui:  " ,json.dumps(msg,indent=4))

    requests.post(api_url, headers = HEADERS, json=msg)
    # Result_id = response.json()
    # if config_info['DEFAULT']['DEBUG'] == "on":
    #     print(json.dumps(Result_id,indent=4))
    return ''

# if __name__ == "__main__":
#     GetConfig()
#     GetExecution()
#     print(json.dumps(next_execution,indent=4))
#     SendPartialResult()

def main_cycle():
    global CONFIG_OF_EXP
    global next_execution
    global status_config
    global Working
    if CONFIG_OF_EXP != None:
        if config_info['DEFAULT']['DEBUG'] == "on":
            print("Esta a passar pelo if none este\n")
        while True:
            if not Working:
                if config_info['DEFAULT']['DEBUG'] == "on":
                    print("Esta a passar pelo if none\n")
                GetExecution()
                if test:
                    print("\n\nIsto_1 :")
                    print (next_execution)
            time.sleep(0.5)
            if ("config" in next_execution.keys()) and (not Working) and next_execution["config"]!=None:
                save_execution =next_execution.get("config",None)
                if save_execution != None:
                    print(json.dumps(save_execution))
                # if save_execution != None:                                 # Estava a passar em cima e não sei bem pq
                    status_config=Send_Config_to_Pic(next_execution)
                if test:
                    print("O valor do Working é: "+str(Working))
            # pass
            # print("teste 12")
            # print(Working)

    return ''

if __name__ == "__main__":
    BASE_API_URL = config_info['DEFAULT']['SERVER'] + "/api/v1/"
    print("[Starting] Experiment Server Starting...")
    # global next_execution
    connected = None
    interface = importlib.import_module("pic_interface.interface")
    while True:
        try:
            GetConfig()
            print ("all good")
            if interface.do_init(CONFIG_OF_EXP["config"],config_info['DEFAULT']['DEBUG']) :
                print("Experiment "+CONFIG_OF_EXP["config"]['id']+" Online !!")
                main_cycle()
            else:
                print ("Experiment not found")
        except serial.SerialException:
            print("*ERROR: Could not open serial port. Trying again after 10s...")
            time.sleep(10)
        except:
            #LOG ERROR
            print("Failed connecting to FREE server. Trying again after 10s...")
            #So faz shutdown do socket se este chegou a estar connected
            time.sleep(10)



# global CONFIG_OF_EXP
# global interface
# interface = importlib.import_module("pic_interface.interface")
# print("Recebi mensagem de configuracao. A tentar inicializar a experiencia\n")
# CONFIG_OF_EXP = myjson['config_file']

# #LIGAR A DISPOSITIVO EXP - INIT
# #Talvez passar erros em forma de string JSON para incluir no reply em vez de OK e NOT OK
# if interface.do_init(CONFIG_OF_EXP) :
#     send('{"reply_id": "1", "status":"Experiment initialized OK"}')

# else :
#     send('{"reply_id": "1", "error":"-1", "status":"Experiment initialized NOT OK"}')
