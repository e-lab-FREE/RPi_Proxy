import socket
import json
import importlib
import threading
import time
import requests
import pprint

SERVER = "194.210.159.33"
MY_IP = "192.168.1.83"
NAME = "Monte_Carlo"
SEGREDO = "estou bem"
CONFIG_OF_EXP = []
SEGREDO = "estou bem"

def GetConfigFile():
    api_url = "http://"+SERVER+":8001/getConfig"
    todo = {"id_RP": MY_IP, "segredo": SEGREDO}
    response =  requests.post(api_url, json=todo)
    CONFIG_OF_EXP = response.json()
    print(json.dumps(CONFIG_OF_EXP['config_file'],indent=4))

def GetExperiment():
    api_url = "http://"+SERVER+":8001/getExperiment"
    todo = {"name":"Monte_Carlo"}
    response =  requests.post(api_url, json=todo)
    print (response.json())


def SendResult():
    api_url = "http://"+SERVER+":8001/sendResult?name="+str(NAME)
    todo = {"msg_id":"11","data":{"val:":"1","temp":"28"}}
    response =  requests.post(api_url, json=todo)
    print (response.json())



if __name__ == "__main__":
    SendResult()


# penso que isto devia ter um endpoint para o main server chamar quando for necessario 
# inicar a exp e a dar o status ? em vez de spamar o server com requests de 30ms em 30ms
#  