#!/usr/bin/python3

import serial
import json
import re

import pic_interface.PPT200 as PPT200
import pic_interface.Arinst as Arinst
import pic_interface.GPIO as GPIO
import pic_interface.Cavity as Cavity

serial_port = None
list_of_ports = {}
#status, config

def print_serial():
    global serial_port

    while True:
        pic_message = serial_port.read_until(b'\r')
        pic_message = pic_message.decode(encoding='ascii')
        if len(pic_message.strip()) > 1: #Apanha os casos em que o pic manda /n/r
            print(pic_message.strip())

def receive_data_from_exp(conn,HEADERS,config_info,config):
    global list_of_ports
    return Cavity.Do_experiment(conn,HEADERS,config_info,config["id"],list_of_ports["pressure_gage"], list_of_ports["arinst"],config["config"]["f_strat"]*10**6, config["config"]["f_end"]*10**6, config["config"]["f_step"]*10**6, config["config"]["n_iteration"], config["config"]["back_pressure"]/100,config["config"]["pressure"],config["config"]["gas_selector"],config["config"]["discharge"],config["config"]["magnetic_field"])
    
#ALGURES AQUI HA BUG QUANDO NAO ESTA EM NENHUMA DAS PORTAS
def try_to_lock_experiment(component, serial_port):
    #LOG_INFO
    if component == "pressure_gage":
        try:
            print("checking: pressure_gage")
            PPT200.get_pressure(serial_port)
            return True
        except:
            print("error: pressure_gage")
            return False
    elif component == "arinst":
        try:  
            print("checking: arinst")
            Arinst.Test_Arinst(serial_port, 3008000000, 3391000000, 500000, 1)
            return True
        except:
            print("error: arinst")
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
def do_init(config_json,dbug):
    global serial_port
    global list_of_ports
    print("Aqui")
    if 'serial_port' in config_json:
        print("entrou")
        for exp_port in config_json['serial_port'].keys():
            print("A tentar abrir a porta "+config_json['serial_port'][exp_port]["port"]+"\n")
            try:
                #alterar esta função para aceitar mais definições do json
                #é preciso uma função para mapear os valores para as constantes da porta série
                #e.g. - 8 bits de data -> serial.EIGHTBITS; 1 stopbit -> serial.STOPBITS_ONE
                serial_port = serial.Serial(port = config_json['serial_port'][exp_port]["port"],\
                                                    baudrate=int(config_json['serial_port'][exp_port]['baud']),\
                                                    timeout = int(config_json['serial_port'][exp_port]['death_timeout']))
            except serial.SerialException:
                
                #LOG_WARNING: couldn't open serial port exp_port. Port doesnt exist or is in use
                pass
            else:
                if try_to_lock_experiment(exp_port, serial_port) :
                    list_of_ports[exp_port]=serial_port
                else:
                    serial_port.close()
        if serial_port.is_open :
            #LOG_INFO : EXPERIMENT FOUND. INITIALIZING EXPERIMENT
            print("Consegui abrir a porta e encontrar a experiencia\n")
            GPIO.Int_GPIO()
            #Mudar para números. Return 0 e mandar status
            return True
        else:
            #SUBSTITUIR POR LOG_ERROR : couldn't find the experiment in any of the configured serial ports
            print("Nao consegui abrir a porta e encontrar a experiencia\n")
            #return -1
            return False
    else:
        #LOG_ERROR - Serial port not configured on json.
        #return -2
        return False

def do_config(config_json) :
    global serial_port
    return 1, True
    cmd ="cfg\t"+str(config_json["config"]["deltaX"])+"\t"+str(config_json["config"]["samples"])+"\r"
    cmd = cmd.encode(encoding="ascii")
    #Deita fora as mensagens recebidas que não
    #interessam
    serial_port.reset_input_buffer()
    serial_port.write(cmd)
    print("A tentar configurar experiência")
    while True :
        pic_message = serial_port.read_until(b'\r')
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
    return True
    #elif "STOPED" or "CONFIGURED" or "RESETED" in pic_message.decode(encoding='ascii') :
    #    return False
    #Aqui não pode ter else: false senão rebenta por tudo e por nada
    #tem de se apontar aos casos especificos -_-
    

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
