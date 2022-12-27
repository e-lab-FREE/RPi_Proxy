import Main_Cavity as M_C 
import PPT200 as PPT200
import json
import time
import threading

stop = 1
def Mauser_pressure():
    global serial_pressure
    global stop
    while stop:
        pressure = "{:.3f}".format(PPT200.get_pressure(serial_pressure))
        send_message = {"pressure": pressure}
        print(json.dumps(send_message, indent=4))
        time.sleep(0.005)
    return

if __name__ == "__main__":
    data_thread = threading.Thread(target=Mauser_pressure,daemon=True)
    # arnist('/dev/ttyACM0', 3308000000, 3891000000, 500000, 4)
    M_C.Int_GPIO()
    serial_pressure = PPT200.int_com_PPT200('/dev/ttyUSB0')
    data_thread.start()
    # Set Up experiment:
    M_C.Vacum_Pump_stat(1)
    M_C.Inject_Gas(1,0.006)
    M_C.Discharge_stat(1)
    while True:
        if input() == '0':
           stop=0
           M_C.Vacum_Pump_stat(0)
           M_C.Discharge_stat(0)
           break
        else:
            pass 
    
