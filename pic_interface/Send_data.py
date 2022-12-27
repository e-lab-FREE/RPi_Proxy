import requests
import http.client
import json


def SendPartialResult(conn,msg,config_info,HEADERS):
    # print(next_execution)
    api_url = "/api/v1/result"
    if config_info['DEFAULT']['DEBUG'] == "on":
        print(str(msg))
        print(api_url)
        print("Aqui:  " ,json.dumps(msg,indent=4))
    payload = json.dumps(msg)
    conn.request("POST",api_url,payload,headers=HEADERS)
    response = json.loads(conn.getresponse().read().decode('utf8'))
    print(response)
    # Result_id = response.json()
    # if config_info['DEFAULT']['DEBUG'] == "on":
    #     print(json.dumps(Result_id,indent=4))
    return ''
