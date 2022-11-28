#!/usr/bin/python3

import serial
import json
import re
import time
from datetime import datetime, date, time, timedelta


import pic_interface.experiment_details as exp

serial_port = None 
dbuging = "off"
time_point = datetime.now()
dt=1

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
    global dt
    global time_point
    if (dbuging == "on"):
        print("SEARCHING FOR INFO IN THE SERIE PORT\n")
    try:
        pic_message = serial_port.read_until(b'\r')
        pic_message = pic_message.decode(encoding='ascii')
    except:
        print("TODO: send error to server, pic is not conected")
    if (dbuging == "on"):
        print("MENSAGE FORM PIC:\n")
        print(pic_message)
        print("\-------- --------/\n")
    if "DAT" in pic_message:
        print("INFO FOUND\nEXPERIMENTE STARTED")
        time_point = datetime.now()
        return "DATA_START"
    elif "END" in pic_message:
        print("INFO FOUND\nEXPERIMENTE ENDED")
        return "DATA_END"
    else:
        """ AQUI SÃO OS OUTPUTS DA EXPERIÊNÇIA JÁ CONVERTIDOS
               adc_value1       adc_value2       adc_Value3
        Linear function in the form f(x) = slope*x + offset
        adc_Value1: tension ( f(V) =  0.132088*adc_value1 + 66.383)  
        adc_Value2: current ( f(A) =  0.327324*adc_value2 + 36)  
        adc_Value3: pressure gauge value
        """
        print("ENCONTREI INFO\nDADOS NA PORTA")
        if pic_message == None:
           print("Mensagem em branco !!!!!!!!")
           pic_message = serial_port.read_until(b'\r')
           pic_message = pic_message.decode(encoding='ascii')
        
        pic_message = pic_message.strip()
        pic_message = pic_message.split("\t")
        while True:
            try:
                if float(pic_message[2]) < 0.00001 :
                    time_point = time_point +  timedelta(milliseconds=dt)
                else:
                    time_point = time_point +  timedelta(seconds=1)
                pic_message = exp.data_to_json(time_point,pic_message)
                break
            except:
                print("Mensagem em branco __ !!!!!!!!")
                pic_message = serial_port.read_until(b'\r')
                pic_message = pic_message.decode(encoding='ascii')
                pic_message = pic_message.strip()  ## 
                pic_message = pic_message.split("\t") ## correcção do bug 
                # print(pic_message)
        #pic_message = '{"adc_value1": "testing"}'
        return pic_message
    
#ALGURES AQUI HA BUG QUANDO NAO ESTA EM NENHUMA DAS PORTAS
def try_to_lock_experiment(config_json, serial_port):
    print("SEARCHING FOR THE PIC IN THE SERIE PORT")
    try:
        pic_message = serial_port.read_until(b'\r')
        pic_message = pic_message.decode(encoding='ascii')
        pic_message = pic_message.strip()
        print("PIC MENSAGE:\n")
        print(pic_message)
        print("\-------- --------/\n")
    except:
        print("TODO: send error to server, pic is not conected")

    match = re.search(r"^(IDS)\s(?P<exp_name>[^ \t]+)\s(?P<exp_state>[^ \t]+)$",pic_message)
    print(config_json['id'])
    print(match.group("exp_name"))
    if match.group("exp_name") == config_json['id']:
        #LOG_INFO
        print("PIC FOUND ON THE SERIAL PORT")
        if match.group("exp_state") == "STOPED":
            return True
        else:
            print("STATE OF MACHINE DIF OF STOPED")
            if do_stop():
                return True
            else:
                return False
    else:
        #LOG INFO
        print("PIC NOT FOUND ON THE SERIAL PORT")
        return False

#DO_INIT - Abre a ligacao com a porta serie
#NOTAS: possivelmente os returns devem ser jsons com mensagens de erro
#melhores, por exemplo, as portas não existem ou não está o pic em nenhuma
#delas outra hipotese é retornar ao cliente exito ou falha
#e escrever detalhes no log do sistema
def do_init(config_json,dbug):
    global serial_port
    global dbuging
    dbuging = dbug
    if 'serial_port' in config_json:
        for exp_port in config_json['serial_port']['ports_restrict']:
            print("TRYING TO OPEN THE SERIAL PORT: "+exp_port+"\n")
            try:
                #alterar esta função para aceitar mais definições do json
                #é preciso uma função para mapear os valores para as constantes da porta série
                #e.g. - 8 bits de data -> serial.EIGHTBITS; 1 stopbit -> serial.STOPBITS_ONE
                serial_port = serial.Serial(port = exp_port,\
                                                    baudrate=int(config_json['serial_port']['baud']),\
                                                    timeout = int(config_json['serial_port']['death_timeout']))
            except serial.SerialException:
                #LOG_WARNING: couldn't open serial port exp_port. Port doesnt exist or is in use
                print("ERRO: Could not open serial port!!")
                pass
            else:
                if try_to_lock_experiment(config_json, serial_port) :
                    break
                else:
                    serial_port.close()
        
        if serial_port.is_open:
            #LOG_INFO : EXPERIMENT FOUND. INITIALIZING EXPERIMENT
            print("I FOUND THE SERIAL PORT\n")
            #Mudar para números. Return 0 e mandar status
            return True
        else:
            #SUBSTITUIR POR LOG_ERROR : couldn't find the experiment in any of the configured serial ports
            print("I COULDN'T OPEN THE DOOR AND FIND THE EXPERIENCE\n")
            #return -1
            return False
    else:
        #LOG_ERROR - Serial port not configured on json.
        #return -2
        return False

def do_config(config_json) :
    global serial_port
    global dt 
    dt = int(int(config_json["config"]["sigperiod"])/int(config_json["config"]["numsamps"]))
    if dt == 0:
        dt = 1
    cmd = exp.msg_to_config_experiment(config_json)
    if cmd is not False:
        serial_port.reset_input_buffer()
        serial_port.write(cmd)
    else:
        print("ERROR: on the config of the experiment")
        return -1, False 
    #Deita fora as mensagens recebidas que não
    #interessam
    
    print("A tentar configurar experiência")
    while True :
        pic_message = serial_port.read_until(b'\r')
        print(pic_message)
        print("MENSAGEM DO PIC DE CONFIGURACAO:\n")
        print(pic_message.decode(encoding='ascii'))
        print("\-------- --------/\n")
        if "CFG" in pic_message.decode(encoding='ascii') :
            pic_message = pic_message.decode(encoding='ascii')
            #Remover os primeiros 4 caracteres para tirar o "CFG\t" 
            pic_message = pic_message[4:]
            pic_message = pic_message.replace("\t"," ")
            break
        elif re.search(r"(STOPED|RESETED){1}$",pic_message.decode(encoding='ascii')) != None:
            return -1,False
    status_confirmation = serial_port.read_until(b'\r')
    status_confirmation = status_confirmation.decode(encoding='ascii')
    print("MENSAGEM DO PIC A CONFIRMAR CFGOK:\n")
    print(status_confirmation)
    print("\-------- --------/\n")
    if "CFGOK" in status_confirmation:
        return pic_message, True
    else:
        return -1, False

def do_start() :
    global serial_port

    print("Try to start the experiment\n")
    
    cmd = "str\r"
    cmd = cmd.encode(encoding='ascii')
    serial_port.reset_input_buffer()
    serial_port.write(cmd)
    while True :
        pic_message = serial_port.read_until(b'\r')
        print("MENSAGEM DO PIC A CONFIRMAR STROK:\n")
        print(pic_message.decode(encoding='ascii'))
        print("\-------- --------/\n")
        if "STROK" in pic_message.decode(encoding='ascii') :
            return True
        elif re.search(r"(STOPED|CONFIGURED|RESETED){1}$",pic_message.decode(encoding='ascii')) != None:
            # print("OOOO")
            return False
        
        #elif "STOPED" or "CONFIGURED" or "RESETED" in pic_message.decode(encoding='ascii') :
        #    return False
        #Aqui não pode ter else: false senão rebenta por tudo e por nada
        #tem de se apontar aos casos especificos -_-
    

def do_stop() :
    global serial_port
    
    print("Try to stop the experiment\n")
    cmd = "stp\r"
    cmd = cmd.encode(encoding='ascii')
    serial_port.reset_input_buffer()
    serial_port.flush()
    serial_port.write(cmd)
    while True :
        try:
            pic_message = serial_port.read_until(b'\r')
            print("MENSAGEM DO PIC A CONFIRMAR STPOK:\n")
            print(pic_message.decode(encoding='ascii'))
            print("\-------- ! --------/\n")
            print ( pic_message.decode(encoding='ascii').split("\t"))
        except:
            pass
        if "STPOK" in pic_message.decode(encoding='ascii') :
            return True
        # elif "STP" in pic_message.decode(encoding='ascii') :
        #     print("Reading the STP  send to the pic")
        #     pass
        elif len(pic_message.decode(encoding='ascii').split("\t")) == 3 and  pic_message.decode(encoding='ascii').split("\t")[2] in ["CONFIGURED\r","RESETED\r"] :
        # elif re.search(r"(CONFIGURED|RESETED){1}$",pic_message.decode(encoding='ascii')) != None :
            print("There is garbage in the serial port try the command again!")
            serial_port.reset_input_buffer()
            serial_port.write(cmd)
            # Maybe create a counter to give a time out if the pic is not working correct
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
