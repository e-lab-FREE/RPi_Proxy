


def msg_to_config_experiment(config_json):
    try:
        cmd ="cfg\t"+str(config_json["config"]["deltaX"])+"\t"+str(config_json["config"]["samples"])+"\r"
        cmd = cmd.encode(encoding="ascii")
        return cmd 
    except:
        print("TODO: send error to server, pic is not conected")
        return False 

def data_to_json(pic_message):
    return {"Sample_number":str(pic_message[0]),\
            "Val1":str(pic_message[1]),\
            "Val2":str(pic_message[2]),\
            "Val3":str(pic_message[3]),\
            "Val4":str(pic_message[4])}
    
