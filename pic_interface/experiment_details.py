from datetime import datetime

def msg_to_config_experiment(config_json):
    try:
        cmd ="cfg\t"+str(int(float(config_json["config"]["max_duty"]) * 6.429 + 14.286))+\
            "\t"+str(int(config_json["config"]["sigperiod"] * 50 + 0.0))+\
            "\t"+str(config_json["config"]["numsamps"]) +\
            "\t"+str(config_json["config"]["numperiod"])+\
            "\t"+str(int(config_json["config"]["pressure"] * 100 + 0.0)) +\
            "\t"+str(int(config_json["config"]["pump_press"] * 100 + 0.0))+\
            "\t"+str(config_json["config"]["gas_selector"])+\
            "\r"
        cmd = cmd.encode(encoding="ascii")
        return cmd 
    except:
        print("TODO: send error to server, pic is not conected")
        return False 

def data_to_json(time_data,pic_message):
    print(pic_message[0])
    print(pic_message[1])
    return {"time":str(time_data),\
            "adc_value1":str(0.132088*float(pic_message[0]) - 66.383),\
            "adc_value2":str(0.327324 * float (pic_message[1]) - 36),\
            "adc_value3":str(pic_message[2])}