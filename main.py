import requests
import json
from datetime import datetime
import importlib
import threading
import time
import configparser
import serial
import json
import re
import pic_interface.VSR53USB as VUSB

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

'''
 Inport the information about the:
 [DEFAULT]  
    DEBUG = on 
 [FREE]
    SERVER = elab.vps.tecnico.ulisboa.pt
    PORT = 8003
 [APPARATUS]
    ID= 1
    SECRET = super_secret

'''

# Prevent ConfigParser interpolation of values
ini_file = configparser.ConfigParser(interpolation=None)
ini_file.read('server_info.ini')

'''
Comunication URL and Endpoints of FREE server
'''

# Base_URL = ini_file['FREE']['PROTOCOL']+"://"+ini_file['FREE']['SERVER']+":"+ini_file['FREE']['PORT']+"/api/"+API_Version
ListOfEndpoints={
    
    "aparatus":   {
        "deflaut" : "/apparatus/"+ini_file['APPARATUS']['ID'],
        "next": "/nextexecution",            
    },
    "execution" : { 
        "deflaut" :"/execution/",
        "status" : "/status"
    },
    "result" : "/result",
    "version": "/version"
}


CONFIG_OF_EXP = []
next_execution = {}
SAVE_DATA = []
SEND_NT = []
LIST_OF_TRUE= ['true','1','yes','y','t','https']

time_check_execuition = 5 # sec

partial_total = 20

test =False
Working = False

interface = None

lock = threading.Lock()

new_pressure_gauge = None
new_pressure = 0
EXP_RUNING = True
#new_pressure = 0


'''
 ----- Comunications with FREE SERVER -----
'''
class ComunicatedWithFREEServer:
    FREE_Version = "0.6.0"
    API_Version = "v1"
    ListOfEndpoints={
        "aparatus":   {
            "deflaut" : "/apparatus/"+ini_file['APPARATUS']['ID'],
            "next": "/nextexecution",            
        },
        "execution" : { 
            "deflaut" :"/execution/",
            "status" : "/status"
        },
        "result" : "/result",
        "version": "/version"
    }

    def __init__(self,ini_file):
        if ini_file['FREE']['HTTPS'].lower() in LIST_OF_TRUE:
            self.URL = "https://"
        else:
            self.URL = "http://"
        self.URL += ini_file['FREE']['SERVER']+":"+ini_file['FREE']['PORT']+"/api/"+self.API_Version
        self.Headers = { 
            "Authentication": str(ini_file['APPARATUS']['SECRET']), 
            "Content-Type": "application/json"
            }
        self.ExecutionConfig = 0
        return

    def UpdateExecutionConfig(self):
        
        return

    def SendREQUEST(self,end_point,request_type,send_JSON={}):
        if ini_file['DEFAULT']['DEBUG'] == "on:":
            print("trying to send info to the "+self.URL)
            if send_JSON.keys() != None:
                print(str(send_JSON))
                print("Sending JSON: \n\r" ,json.dumps(send_JSON,indent=4))
        else:
            pass

        try:
            if request_type == "GET":
                response = requests.get(self.URL+end_point,headers = self.Headers, verify=False)
            elif request_type == "POST":
                response = requests.post(self.URL+end_point, headers = self.Headers, json=send_JSON, verify=False)
            elif request_type == "PATCH":
                response = requests.patch(self.URL+end_point, headers =self.Headers,json=send_JSON, verify=False)
        except:
            print("ERROR: Fail to comunicated: "+ request_type+" With URL: "+self.URL+end_point)
        
        if ini_file['DEFAULT']['DEBUG'] == "on":
            print(json.dumps(response.json(),indent=4))

        return response.json()
    
    def VerifyVersionFREE(self):

        api_url = ListOfEndpoints['version']
        
        response =  self.SendREQUEST(api_url,"GET")

        if response['version'] == self.FREE_Version:
            return  True, response['version']
        else: 
            return False, response['version']



def GetConfig(ComFREE):
    global CONFIG_OF_EXP

    api_url = ListOfEndpoints['aparatus']['deflaut']

    response = ComFREE.SendREQUEST(api_url,"GET")

    CONFIG_OF_EXP = response

    return ''

def GetExecution(ComFREE):

    api_url = ListOfEndpoints['aparatus']['deflaut']+ListOfEndpoints['aparatus']['next']

    response = ComFREE.SendREQUEST(api_url,"GET")

    if (response['protocol']['config'] !=None):
        print(json.dumps(response,indent=4))

    return response


def SendInfoAboutExecution(ComFREE,id,info):

    api_url = ListOfEndpoints['execution']['deflaut']+str(id)+ListOfEndpoints['execution']['status']
    
    response = ComFREE.SendREQUEST(api_url,"PATCH",{"status": info})

    return ''

def SendResult(ComFREE,msg):

    api_url = ListOfEndpoints['result']
   
    ComFREE.SendREQUEST(api_url,"POST",msg)

    return ''





'''
 ----- Comunications with the Experiment Apparatus -----
'''

def read_pressure():
    global new_pressure
    global new_pressure_gauge
    global EXP_RUNING
    while EXP_RUNING:
        new_pressure = float(new_pressure_gauge.Pressure().decode('ascii'))
        time.sleep(0.001)
    return

def send_exp_data(COMfree,next_execution_id):
    global SAVE_DATA
    global Working
    global lock
    global next_execution
    global SEND_NT
    global partial_total
    global new_pressure
    global EXP_RUNING

    inte_send=0
    while interface.receive_data_from_exp() != "DATA_START":
        inte_send=0
        pass
    #event = Event()
    EXP_RUNING = True
    pressure_thread = threading.Thread(target=read_pressure,args=(),daemon=True)
    pressure_thread.start()
    SendInfoAboutExecution(COMfree,int(next_execution_id),"R")
    while True:
        exp_data = interface.receive_data_from_exp()
        if ini_file['DEFAULT']['DEBUG'] == "on":
            print("What pic send on serial port (converted to json): ",json.dumps(exp_data,indent=4))
        try:
            exp_data = json.loads(exp_data)
        except:
            pass
        try:
            exp_data["new_pressure_gauge"] = round(new_pressure,4)
        except:
            pass
        if exp_data != "DATA_END":
            
            SAVE_DATA.append(exp_data)
            if float(exp_data["adc_value3"]) < 0.00001:
                SEND_NT.append(exp_data)
                inte_send = inte_send +1
                if inte_send >= partial_total : # falta verificar que ja estamos na execução da sonda em si (não a fazer vacum)
                    inte_send = 0
                    send_message = {"execution":int(next_execution_id),"value":SEND_NT,"result_type":"p"}#,"status":"running"}
                    SEND_NT = []
                    SendResult(COMfree,send_message)
            else:
                SEND_NT.append(exp_data)
                send_message = {"execution":int(next_execution_id),"value":SEND_NT,"result_type":"p"}#,"status":"running"}
                SEND_NT = []
                SendResult(COMfree,send_message)
        else:
            if SEND_NT != []:
                send_message = {"execution":int(next_execution_id),"value":SEND_NT,"result_type":"p"}#,"status":"running"}
                SEND_NT = []
                SendResult(COMfree,send_message)
            send_message = {"execution":int(next_execution_id),"value":[],"result_type":"f"}
            SendResult(COMfree,send_message)
            Working = False
            next_execution = {}
            SAVE_DATA=[]
            #event.set()
            EXP_RUNING = False
            interface.do_stop()
            time.sleep(0.00001)
            return 


def Send_Config_to_Pic(COMfree,myjson):
    global Working
    global partial_total

    print("Recebi mensagem de configurestart. A tentar configurar pic")
    actual_config, config_feita_correcta = interface.do_config(myjson)
    if config_feita_correcta :   #se config feita igual a pedida? (opcional?)
        print(myjson["id"])
        # SendInfoAboutExecution(myjson["id"],"R")
        partial_total = int(int(myjson["config"]["sigperiod"])/int(myjson["config"]["numsamps"]))*300 # dt que o user pediu  * 300 ms de aquisição.
        if partial_total == 0:
            partial_total = 300
        data_thread = threading.Thread(target=send_exp_data,args=(COMfree,myjson["id"],),daemon=True)
        print("PIC configurado.\n")
        if interface.do_start(): 
            Working = True
            data_thread.start()
            time.sleep(0.000001)
            #O JSON dos config parameters está mal e crasha o server. ARRANJAR
            #send_mensage = '{"reply_id": "2","status":"Experiment Running","config_params":"'+str(myjson["config_params"])+'}'
            # Working = True
        else :
            SendInfoAboutExecution(COMfree,myjson["id"],"E")
    
    else:
        SendInfoAboutExecution(COMfree,myjson["id"],"E")
    return ''



'''
----- Main Cycle -----
'''


def MainCycle(COMfree):
    global CONFIG_OF_EXP
    global Working
    global next_execution
    global new_pressure_gauge

    if CONFIG_OF_EXP != None:
        if ini_file['DEFAULT']['DEBUG'] == "on":
            print("Esta a passar pelo if none este\n")
        while True:
            time.sleep(time_check_execuition)
            if not Working:
                if ini_file['DEFAULT']['DEBUG'] == "on":
                    print("Esta a passar pelo if none\n")
                next_execution = GetExecution(COMfree)
                if test:
                    print (next_execution)
            # time.sleep(1)
            if ("config" in next_execution.keys()) and (not Working) and next_execution["config"]!=None:
                print("here") 
                print("Gas_selector = "+str(next_execution["config"]["gas_selector"]))
                new_pressure_gauge.Adj_Gas_Correctoion_Factor(next_execution["config"]["gas_selector"])
                status_config = Send_Config_to_Pic(COMfree,next_execution)
                if ini_file['DEFAULT']['DEBUG'] == "on":
                    print(status_config)
            else:
                pass

    return ''

if __name__ == "__main__":
    connected = None
    interface = importlib.import_module("pic_interface.interface")

    print("Checking Version...")
    COMfree = ComunicatedWithFREEServer(ini_file)
    while True:
        try:
            True_False, Server_Version = COMfree.VerifyVersionFREE()
            if True_False :
                print("\nVersion match!!\n ")
                print("[Starting] Experiment Server Starting...")
                GetConfig(COMfree)
                print ("all good")
                if interface.do_init(CONFIG_OF_EXP["config"],ini_file['DEFAULT']['DEBUG']) :
                    new_pressure_gauge = VUSB.VSR53USB({"COM":'/dev/tty_pressure',"timeout":1})
                    print("Experiment "+CONFIG_OF_EXP["config"]['id']+" Online !!")
                    MainCycle(COMfree)
                    time.sleep(0.3)
                else:
                    print ("Experiment not found")
            else:
                print("Proxy Version is "+COMfree.FREE_Version+" and is diferent them FREE Server Version "+Server_Version)
        except:
            #LOG ERROR
            print("Faill to connect to the Server. trying again after 10 s")
            #So faz shutdown do socket se este chegou a estar connected
            time.sleep(10)
