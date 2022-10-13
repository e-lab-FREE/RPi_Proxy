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
# next_execution = {}
SAVE_DATA = []

test =False
Working = False

interface = None

lock = threading.Lock()



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
        if ini_file['FREE']['HTTPS'] == True:
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
            print("Trying to send info to the "+self.URL)
            if send_JSON.keys() != None:
                print(str(send_JSON))
                print("Sending JSON: \n\r" ,json.dumps(send_JSON,indent=4))
        else:
            pass

        try:
            if request_type == "GET":
                response = requests.get(self.URL+end_point,headers = self.Headers)
            elif request_type == "POST":
                response = requests.post(self.URL+end_point, headers = self.Headers, json=send_JSON)
            elif request_type == "PATCH":
                response = requests.patch(self.URL+end_point, headers =self.Headers,json=send_JSON)
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

    if (response.json()['protocol']['config'] !=None):
        print(response)
        next_execution = response

    return next_execution


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

def send_exp_data(next_execution):
    global SAVE_DATA
    global Working
    global lock

    while interface.receive_data_from_exp() != "DATA_START":
        pass
    SendInfoAboutExecution(int(next_execution["id"]),"R")
    while True:
        exp_data = interface.receive_data_from_exp()
        if ini_file['DEFAULT']['DEBUG'] == "on":
            print("What pic send on serial port (converted to json): ",json.dumps(exp_data,indent=4))
        try:
            exp_data = json.loads(exp_data)
        except:
            pass
        if exp_data != "DATA_END":
            
            SAVE_DATA.append(exp_data)
            send_message = {"execution":int(next_execution["id"]),"value":exp_data,"result_type":"p"}#,"status":"running"}
            SendResult(send_message)
        else:
            send_message = {"execution":int(next_execution["id"]),"value":SAVE_DATA,"result_type":"f"}
            SendResult(send_message)
            Working = False
            next_execution = {}
            SAVE_DATA=[]
            time.sleep(0.00001)
            return 


def Send_Config_to_Pic(myjson):
    global Working

    print("Recebi mensagem de configurestart. A tentar configurar pic")
    actual_config, config_feita_correcta = interface.do_config(myjson)
    if config_feita_correcta :   #se config feita igual a pedida? (opcional?)
        print(myjson["id"])
        # SendInfoAboutExecution(myjson["id"],"R")
        data_thread = threading.Thread(target=send_exp_data,args=(myjson,),daemon=True)
        print("PIC configurado.\n")
        if interface.do_start(): 
            Working = True
            data_thread.start()
            time.sleep(0.000001)
            #O JSON dos config parameters está mal e crasha o server. ARRANJAR
            #send_mensage = '{"reply_id": "2","status":"Experiment Running","config_params":"'+str(myjson["config_params"])+'}'
            # Working = True
        else :
            SendInfoAboutExecution(myjson["id"],"E")
    
    else:
        SendInfoAboutExecution(myjson["id"],"E")
    return ''



'''
----- Main Cycle -----
'''


def MainCycle():
    global CONFIG_OF_EXP
    global Working

    if CONFIG_OF_EXP != None:
        if ini_file['DEFAULT']['DEBUG'] == "on":
            print("Esta a passar pelo if none este\n")
        while True:
            if not Working:
                if ini_file['DEFAULT']['DEBUG'] == "on":
                    print("Esta a passar pelo if none\n")
                next_execution = GetExecution(COMfree)
                if test:
                    print("\n\nIsto_1 :")
                    print (next_execution)
            time.sleep(0.5)
            if ("config" in next_execution.keys()) and (not Working) and next_execution["config"]!=None:
                # Estava a passar em cima e não sei bem pq 
                status_config=Send_Config_to_Pic(next_execution)
                if ini_file['DEFAULT']['DEBUG'] == "on":
                    print(status_config)

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
                    print("Experiment "+CONFIG_OF_EXP["config"]['id']+" Online !!")
                    MainCycle(COMfree)
                else:
                    print ("Experiment not found")
            else:
                print("Proxy Version is "+COMfree.FREE_Version+" and is diferent them FREE Server Version "+Server_Version)
        except:
            #LOG ERROR
            print("Faill to connect to the Server. Trying again after 10 s")
            #So faz shutdown do socket se este chegou a estar connected
            time.sleep(10)
