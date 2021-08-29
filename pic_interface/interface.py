#!/usr/bin/python3

from time import sleep
import serial
import json
import re
import random
import math 
  

serial_port = None
size = None
n_points = None
frist = 1
i = 1
total_in = 0
#status, config

def print_serial():
    global serial_port

    while True:
        pic_message = serial_port.read_until(b'\r')
        pic_message = pic_message.decode(encoding='ascii')
        if len(pic_message.strip()) > 1: #Apanha os casos em que o pic manda /n/r
            print(pic_message.strip())

def receive_data_from_exp():
    global serial_port
    global frist 
    global i 
    global total_in
    if frist == 1:
        frist =0
        return "DATA_START"
    if int(i) > int(n_points):
        sleep(0.01)
        print("Pi: %lf"%(float(total_in)*4/float(n_points)))
        return "DATA_END"
    sleep(0.01)
    
    x = random.random()*float(size)
    y = random.random()*float(size)
    if math.sqrt(x*x+y*y) <=int(size):
        c_in = 1
        total_in = total_in + 1
    else:
        c_in = 0
    pic_message = '{"Sample_number":"'+str(i)+'","eX":"'+str(x)+'","eY":"'+str(y)+'","circ":"'+str(c_in)+'"}'
    # print (i)
    i=i+1
    return pic_message
    
#ALGURES AQUI HA BUG QUANDO NAO ESTA EM NENHUMA DAS PORTAS
def try_to_lock_experiment(config_json, serial_port):
    #LOG_INFO
    print("AH PROCURA DO PIC NA PORTA SERIE")
    pic_message = serial_port.read_until(b'\r')
    pic_message = pic_message.decode(encoding='ascii')
    pic_message = pic_message.strip()
    print("MENSAGEM DO PIC:\n")
    print(pic_message)
    print("\-------- --------/\n")
    match = re.search(r"^(IDS)\s(?P<exp_name>[^ \t]+)\s(?P<exp_state>[^ \t]+)$",pic_message)
    if match.group("exp_name") == config_json['id']:
        #LOG_INFO
        print("ENCONTREI O PIC QUE QUERIA NA PORTA SERIE")
        if match.group("exp_state") == "STOPED":
            return True
        else:
            if do_stop():
                return True
            else:
                return False
    else:
        #LOG INFO
        print("NAO ENCONTREI O PIC QUE QUERIA NA PORTA SERIE")
        return False

#DO_INIT - Abre a ligacao com a porta serie
#NOTAS: possivelmente os returns devem ser jsons com mensagens de erro
#melhores, por exemplo, as portas não existem ou não está o pic em nenhuma
#delas outra hipotese é retornar ao cliente exito ou falha
#e escrever detalhes no log do sistema
def do_init(config_json):
    global serial_port
    
    if 'test_rpi' in config_json:
        print("Isto é uma função de teste!\n")
        return True
    else:
        #LOG_ERROR - Serial port not configured on json.
        #return -2
        print("Falta serial config!\n")
        return False

def do_config(config_json) :
    global serial_port

    global size
    global n_points
    

    print(config_json)
    size = config_json["config_params"]["R"]
    n_points = config_json["config_params"]["Iteration"]

    print("Size :")
    print(size)
    print("\n")
    print("Numbero de pontos :")
    print(n_points)


    return  config_json,True


def do_start() :
    global serial_port
    global frist
    global i
    global total_in
    total_in = 0 
    i = 1
    frist = 1

    return True

def do_stop() :
    global serial_port

    print("A tentar parar experiencia\n")
    cmd = "stp\r"
    cmd = cmd.encode(encoding='ascii')
    serial_port.reset_input_buffer()
    serial_port.write(cmd)
    while True :
        pic_message = serial_port.read_until(b'\r')
        print("MENSAGEM DO PIC A CONFIRMAR STPOK:\n")
        print(pic_message.decode(encoding='ascii'))
        print("\-------- --------/\n")
        if "STPOK" in pic_message.decode(encoding='ascii') :
            return True
        elif re.search(r"(CONFIGURED|RESETED){1}$",pic_message.decode(encoding='ascii')) != None :
            return False
        #Aqui não pode ter else: false senão rebenta por tudo e por nada
        #tem de se apontar aos casos especificos -_-
        
    

def do_reset() :
    global serial_port

    print("A tentar fazer reset da experiencia\n")
    cmd = "rst\r"
    cmd = cmd.encode(encoding='ascii')
    serial_port.reset_input_buffer()
    serial_port.write(cmd)
    while True :
        pic_message = serial_port.read_until(b'\r')
        print("MENSAGEM DO PIC A CONFIRMAR RSTOK:\n")
        print(pic_message.decode(encoding='ascii'))
        print("\-------- --------/\n")
        if "RSTOK" in pic_message.decode(encoding='ascii') :
            return True
        elif re.search(r"(STOPED|CONFIGURED){1}$",pic_message.decode(encoding='ascii')) != None :
            return False
        #Aqui não pode ter else: false senão rebenta por tudo e por nada
        #tem de se apontar aos casos especificos -_-

#get_status placeholder
def get_status():
    global serial_port

    print("Esta funcao ainda nao faz nada\n")
    return True



if __name__ == "__main__":
    import sys
    import threading
    
    fp = open("./exp_config.json","r")
    config_json = json.load(fp)
    #config_json = json.loads('{}')
    if not do_init(config_json):
        sys.exit("Não deu para abrir a porta. F")
    printer_thread = threading.Thread(target=print_serial)
    printer_thread.start()
    while True:
        cmd = input()+"\r"
        cmd = cmd.encode(encoding='ascii')
        serial_port.write(cmd)