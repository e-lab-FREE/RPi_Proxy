#!/usr/bin/python3

import socket
import json
import importlib
import threading
import time

interface = None

HEADER = 64
PORT = 5050
BINARY_DATA_PORT = 5051
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.1.102"
ADDR = (SERVER, PORT)

CONFIG_OF_EXP = []
MY_IP = "192.168.1.83"
SEGREDO = "estou bem"
SAVE_DATA = []

def send_exp_data():
    global SAVE_DATA
    while interface.receive_data_from_exp() != "DATA_START":
        pass
    send_message = '{"msg_id":"11","timestamp":"'+str(time.time_ns())+'","status":"Experiment Starting","Data":""}'
    send(send_message)
    while True:
        exp_data = interface.receive_data_from_exp()
        print(exp_data)
        if exp_data != "DATA_END":
            SAVE_DATA.append('{"timestamp":"'+str(time.time_ns())+'","Data":'+str(exp_data)+'}')
            send_message = '{"msg_id":"11","timestamp":"'+str(time.time_ns())+'","status":"running","Data":'+str(exp_data)+'}'
            send(send_message)
        else:
            send_message = '{"msg_id":"11","timestamp":"'+str(time.time_ns())+'","status":"Experiment Ended","Data":""}'
            send(send_message)
            send_message = '{"msg_id":"7", "results":'+str(SAVE_DATA).replace('\'', '')+'}'
            send(send_message)
            return #EXPERIMENT ENDED; END THREAD


def check_reply(myjson):
        reply_msg = myjson['reply_id']

        if(reply_msg == '6'):
            if 'error' in myjson :
                print ("Error in the reply_id: "+reply_msg+ 'type of error: '+ myjson['status']+ ' ERROR MSG: ' + myjson['error'])
            else:
                print ("reply_id = "+reply_msg+ ' MSG : ' + myjson['info'])
            return True
        else: #INVALID MESSAGE
            return False

def wait_for_messages():
    msg_length = client.recv(HEADER, socket.MSG_WAITALL)
    if msg_length != b'':
        msg_length = int(msg_length)
        msg = client.recv(msg_length, socket.MSG_WAITALL).decode(FORMAT)
        if msg != b'':
            myjson = json.loads(msg)
            if 'msg_id' in myjson:
                check_msg(myjson)
            elif 'reply_id' in myjson:
                check_reply(myjson)
            else:
                #LOG_ERROR
                print("Wrong format of mensage\n")
        else:
            raise socket.error
    else:
        raise socket.error


def send(msg):
    try:
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.sendall(send_length)
        #print (send_length)
        #print (message)
        client.sendall(message)
    except socket.error:
        raise socket.error

#erro aqui 
def Send_Config_to_Pid(myjson):
    print("Recebi mensagem de configurestart. A tentar configurar pic")
    actual_config, config_feita_correcta = interface.do_config(myjson)
    if config_feita_correcta :   #se config feita igual a pedida? (opcional?)
        data_thread = threading.Thread(target=send_exp_data,daemon=True)
        print("PIC configurado.\n")
        if interface.do_start():                            #tentar começar experiencia
            print("aqui")
            data_thread.start()
            time.sleep(0.000001)
            #O JSON dos config parameters está mal e crasha o server. ARRANJAR
            #send_mensage = '{"reply_id": "2","status":"Experiment Running","config_params":"'+str(myjson["config_params"])+'}'
            send_mensage = '{"reply_id": "2","status":"Experiment Running"}'
        else :
            send_mensage = '{"reply_id": "2", "error":"-1", "status":"Experiment could not start"}'
    
    else:
        send_mensage = '{"reply_id": "2", "error":"-2", "status":"Experiment could not be configured"}'
    return send_mensage


def check_msg(myjson):
    #print (myjson)
    if  myjson.get('msg_id')!=None:
        msg_id = int( myjson['msg_id'] )
        if ( msg_id == 1): #CONFIG MESSAGE
            global CONFIG_OF_EXP
            global interface
            interface = importlib.import_module("pic_interface.interface")
            print("Recebi mensagem de configuracao. A tentar inicializar a experiencia\n")
            CONFIG_OF_EXP = myjson['config_file']
            
            #LIGAR A DISPOSITIVO EXP - INIT
            #Talvez passar erros em forma de string JSON para incluir no reply em vez de OK e NOT OK
            if interface.do_init(CONFIG_OF_EXP) :
                send('{"reply_id": "1", "status":"Experiment initialized OK"}')

            else :
                send('{"reply_id": "1", "error":"-1", "status":"Experiment initialized NOT OK"}')
        
        elif( msg_id == 2): #CONFIGURESTART MESSAGE
            #DO CONFIG
            if 'error' in myjson:
                print('Existiu um erro na configuração que o user mandou:\n')
                if myjson['error'] == "-1":
                    print('O user passou dos limites num dos seus parametros!!!\n')
                    send_mensage = Send_Config_to_Pid(myjson)
                elif myjson['error'] == "-2":
                    print('O user passou um numero de parametos diferente do que esperado !!!\n')
                    send_mensage = '{"reply_id": "2", "error":"-2", "status":"Experiment could not be configured"}'
            else:
                send_mensage = Send_Config_to_Pid(myjson)
                
            send(send_mensage)    

        elif( msg_id == 3): #STOP MESSAGE
            #DO STOP
            print("Recebi mensagem de stop. A chamar interface do PIC")
            #Assume que do_stop e semelhentes respondem só true ou false.
            #E capaz de ser pouco flexivel
            if interface.do_stop() :
                send_mensage = '{"reply_id": "3","status":"Success. Experiment Stopped"}'
            else:
                send_mensage = '{"reply_id": "3", "error":"-1", "status":"ERROR. Experiment didn\'t Stop"}'
            send(send_mensage)
                
        elif( msg_id == 4):
            #DO RESET
            print("Recebi mensagem de reset. A chamar interface do PIC")
            if interface.do_reset() :
                send_mensage = '{"reply_id": "4","status":"Success. Experiment Reseted"}'
            else:
                send_mensage = '{"reply_id": "4", "error":"-1","status":"ERROR. Experiment didn\'t Reset"}'
            send(send_mensage)
        
        elif( msg_id == 5):
            #READ THE STATUS OF EXP
            print("Recebi mensagem de status. A chamar interface do PIC")
            if interface.get_status() :
                send_mensage = '{"reply_id": "5","status":"Success. Depois aparece aqui o status"}'
            else:
                send_mensage = '{"reply_id": "5", "error":"-1","status":"ERROR. Couldn\'t get status"}'
            send(send_mensage)
        else:
            pass


def IStarted():
    print("Arranquei. A mandar pedido de ligacao ao servidor de experiencias\n")
    send_msg = '{"msg_id": "6","id_RP":"'+str(MY_IP)+'","segredo":"'+str(SEGREDO)+'"}'
    send(send_msg)

def ExperimentResults(Resulte):
    send_msg = '{"msg_id":"7", "results":"'+Resulte+'"}'
    send(send_msg)
    #Não estou a entender de como fazer a pate do erro nesta função preciso de preceber o que o rpi recebe dos PIC's


def SendFile(bin_data) :
    bin_data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bin_data_socket.connect((SERVER, BINARY_DATA_PORT)) #APANHAR ERROS

    bin_data_socket.send(len(bin_data))
    bin_data_socket.send(bin_data)

    reply_size = bin_data_socket.recv(HEADER)
    msg = bin_data_socket.recv(reply_size)

    #Reply message received, comunication is done, close socket
    bin_data_socket.shutdown(socket.SHUT_RDWR)
    bin_data_socket.close()

    #CHECK MESSAGE
    #SEND STATUS TO SERVER

def SendStatus(type_data,timestamp, experiment_status,current_config):
    if type_data == 9:
        send_msg = '{"msg_id":"9", " timestamp":"'+timestamp+'", "experiment_status":"'+ experiment_status +'","current_config":"'+current_config+'"}'
    if type_data == 10:
        send_msg = '{"msg_id":"10", " timestamp":"'+timestamp+'", "id_dados_bin":'+ experiment_status+'"}'
    send(send_msg)

if __name__ == "__main__":
    print("[Starting] Experiment Server Starting...")
    global client
    connected = None
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ADDR)
            connected = True
            IStarted()
            while True:
                    wait_for_messages()
        #APANHAR SÓ EXCEPÇÕES DE LIGAÇÃO
        #AS OUTRAS TÊM DE SER APANHADAS NOS SITIOS CERTOS
        except socket.error as e:
            #LOG ERROR
            print(e)
            print("SOCKET FECHADO OU PARTIDO. A TENTAR ABRIR DE NOVO")
            #So faz shutdown do socket se este chegou a estar connected
            if connected == True :
                client.shutdown(socket.SHUT_RDWR)
                connected = False
            client.close()
            time.sleep(10)
