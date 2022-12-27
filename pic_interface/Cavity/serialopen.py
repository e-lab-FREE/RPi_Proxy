import globals

globals.serialOpen = False
    
def set_SerialOpen(option):
    globals.serialOpen = option
   
    
def get_SerialOpen():
    return globals.serialOpen
