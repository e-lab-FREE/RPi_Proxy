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
LIST_OF_TRUE= ['true','1','yes','y','t','https']
time_check_execuition = 5 # sec

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
        print(self.Headers )
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
            send_JSON=json.loads(send_JSON)
        except:
            pass

        try:
            if request_type == "GET":
                response = requests.get(self.URL+end_point,headers = self.Headers, verify=False)
            elif request_type == "POST":
                response = requests.post(self.URL+end_point, headers = self.Headers, json=send_JSON, verify=False)
            elif request_type == "PATCH":
                response = requests.patch(self.URL+end_point, headers =self.Headers,json=send_JSON, verify=False)
            else:
                print("error")
                return "error"
        except requests.exceptions.Timeout:
    # Maybe set up for a retry, or continue in a retry loop
            print("ERROR: Fail to comunicated: "+ request_type+" With URL: "+self.URL+end_point)
        except requests.exceptions.TooManyRedirects:
    # Tell the user their URL was bad and try a different one
            print("TooManyRedirects")
        except requests.exceptions.RequestException as e:
    # catastrophic error. bail.
            print("RequestException")
            print(e)
        
        if ini_file['DEFAULT']['DEBUG'] == "on":
            try:
                print(json.dumps(response.json(),indent=4))
            except:
                print(response)

        return response.json()
    
    def VerifyVersionFREE(self):

        api_url = ListOfEndpoints['version']
        
        response =  self.SendREQUEST(api_url,"GET")

        if response['version'] == self.FREE_Version:
            return  True, response['version']
        else: 
            return False, response['version']

    def GetConfig(self):
        global CONFIG_OF_EXP

        api_url = ListOfEndpoints['aparatus']['deflaut']

        response = self.SendREQUEST(api_url,"GET")

        CONFIG_OF_EXP = response

        return ''

    def GetExecution(self):

        api_url = ListOfEndpoints['aparatus']['deflaut']+ListOfEndpoints['aparatus']['next']

        response = self.SendREQUEST(api_url,"GET")

        if (response['protocol']['config'] !=None):
            print(json.dumps(response,indent=4))

        return response


    def SendInfoAboutExecution(self,id,info):

        api_url = ListOfEndpoints['execution']['deflaut']+str(id)+ListOfEndpoints['execution']['status']
        
        response = self.SendREQUEST(api_url,"PATCH",{"status": info})

        return ''

    def SendResult(self,msg):

        api_url = ListOfEndpoints['result']
    
        self.SendREQUEST(api_url,"POST",msg)

        return ''

# def GetConfig(ComFREE):
#     global CONFIG_OF_EXP

#     api_url = ListOfEndpoints['aparatus']['deflaut']

#     response = ComFREE.SendREQUEST(api_url,"GET")

#     CONFIG_OF_EXP = response

#     return ''

# def GetExecution(ComFREE):

#     api_url = ListOfEndpoints['aparatus']['deflaut']+ListOfEndpoints['aparatus']['next']

#     response = ComFREE.SendREQUEST(api_url,"GET")

#     if (response['protocol']['config'] !=None):
#         print(json.dumps(response,indent=4))

#     return response


# def SendInfoAboutExecution(ComFREE,id,info):

#     api_url = ListOfEndpoints['execution']['deflaut']+str(id)+ListOfEndpoints['execution']['status']
    
#     response = ComFREE.SendREQUEST(api_url,"PATCH",{"status": info})

#     return ''

# def SendResult(ComFREE,msg):

#     api_url = ListOfEndpoints['result']
   
#     ComFREE.SendREQUEST(api_url,"POST",msg)

#     return ''





'''
 ----- Comunications with the Experiment Apparatus -----
'''

def send_exp_data(COMfree,config_exp):
    global SAVE_DATA
    global Working
    global next_execution
    global lock

    while True:
        exp_data = interface.receive_data_from_exp(COMfree,config_exp)
        if exp_data == True:
            Working = False
            next_execution = {}
            time.sleep(0.00001)
            return

def Send_Config_to_Pic(COMfree,myjson):
    global Working

    print("Recebi mensagem de configurestart. A tentar configurar pic")
    actual_config, config_feita_correcta = interface.do_config(myjson)
    # print(myjson["id"])
    # print("R")
    COMfree.SendInfoAboutExecution(myjson["id"],"R")
    if config_feita_correcta :   #se config feita igual a pedida? (opcional?)
        print(myjson["id"])
        # SendInfoAboutExecution(myjson["id"],"R")
        data_thread = threading.Thread(target=send_exp_data,args=(COMfree,myjson,),daemon=True)
        print("PIC configurado.\n")
        if interface.do_start(): 
            Working = True
            data_thread.start()
            time.sleep(0.000001)
            #O JSON dos config parameters está mal e crasha o server. ARRANJAR
            #send_mensage = '{"reply_id": "2","status":"Experiment Running","config_params":"'+str(myjson["config_params"])+'}'
            # Working = True
        else :
            COMfree.SendInfoAboutExecution(myjson["id"],"E")
    
    else:
        COMfree.SendInfoAboutExecution(myjson["id"],"E")
    return ''



'''
----- Main Cycle -----
'''


def MainCycle(COMfree):
    global CONFIG_OF_EXP
    global Working
    global next_execution

    if CONFIG_OF_EXP != None:
        if ini_file['DEFAULT']['DEBUG'] == "on":
            print("Esta a passar pelo if none este\n")
        while True:
            time.sleep(time_check_execuition)
            if not Working:
                if ini_file['DEFAULT']['DEBUG'] == "on":
                    print("Esta a passar pelo if none\n")
                next_execution = COMfree.GetExecution()
                if test:
                    print (next_execution)
            # time.sleep(1)
            if ("config" in next_execution.keys()) and (not Working) and next_execution["config"]!=None:
                print("here") 
                status_config=Send_Config_to_Pic(COMfree,next_execution)
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
                COMfree.GetConfig()
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
            print("Faill to connect to the Server. trying again after 10 s")
            #So faz shutdown do socket se este chegou a estar connected
            time.sleep(10)
