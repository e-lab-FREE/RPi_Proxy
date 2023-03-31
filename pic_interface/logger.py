import os
import pathlib
from datetime import datetime,date

LOGG_Level = ["OPERATION",\
                  "SERIAL",\
                  "HTTPS",\
                  "ERROR SERIAL",\
                  "ERROR HTTPS"
             ]

'''
----- Write on the .log file -----
'''

def ReportLog(self,log_level,msg):
        pathlib.Path(os.getcwd()+'/logs').mkdir(exist_ok=True) 
        file_name = date.today().strftime("%d-%m-%Y")
        file_path = os.getcwd()+'/logs/'+file_name+".log"
        log = open(file_path, "a")
        log.write(datetime.now().strftime("%H:%M:%S")+" ["+LOGG_Level[log_level]+"] - "+msg+"\n")
        log.close()
        return