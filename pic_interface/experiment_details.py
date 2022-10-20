


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
            "Period":str(pic_message[1]),\
            # "g":str(pic_message[2]),\
            "Velocity":str(pic_message[3]),\
            "Temperature":str(pic_message[4])}
    

