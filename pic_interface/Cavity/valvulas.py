import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)



def int_valvulas():
    GPIO.setup(17, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(5, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(12, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(13, GPIO.OUT, initial=GPIO.HIGH)

    # GPIO.setup(17, GPIO.OUT, initial=GPIO.HIGH)
    # GPIO.setup(17, GPIO.OUT, initial=GPIO.HIGH)
    return


def open_valvulas(valvulas, sleep_time):
    if (int(valvulas)==17):
        GPIO.output(int(valvulas), GPIO.LOW)
        time.sleep(float(sleep_time)*0.001)
        GPIO.output(int(valvulas), GPIO.HIGH)
    if (int(valvulas)==5):
        if(int(sleep_time) == 0):
            GPIO.output(int(valvulas), GPIO.LOW)
        if(int(sleep_time) == 1):
            GPIO.output(int(valvulas), GPIO.HIGH)
    if (int(valvulas)==12):
        if(int(sleep_time) == 0):
            GPIO.output(int(valvulas), GPIO.LOW)
        if(int(sleep_time) == 1):
            GPIO.output(int(valvulas), GPIO.HIGH)
    if (int(valvulas)==13):
        GPIO.output(int(valvulas), GPIO.LOW)
        time.sleep(float(sleep_time)*0.001)
        GPIO.output(int(valvulas), GPIO.HIGH)

    return

