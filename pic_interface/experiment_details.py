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

def data_to_json(pic_message):
    return {"time":str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]),\
            "adc_value1":str(float(0.132088*int(pic_message[0])) - 66.383),\
            "adc_value2":str(float(0.327324 * int (pic_message[1])) - 36),\
            "adc_value3":str(pic_message[2])}