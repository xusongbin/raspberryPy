
# debug done.

import RPi.GPIO as GPIO
import time


KEY1 = 13
KEY2 = 12
KEY3 = 11

KEY_ON = False
KEY_OFF = True

GPIO.setmode(GPIO.BOARD)

GPIO.setup(KEY1, GPIO.IN)
GPIO.setup(KEY2, GPIO.IN)
GPIO.setup(KEY3, GPIO.IN)

key_buf = {KEY1:KEY_OFF, KEY2:KEY_OFF, KEY3:KEY_OFF}

def millis():
    return int(time.time()*1000)

def elapsed(tms):
    return millis()-tms

def get_key(skey):
    pkey = key_buf[skey]
    ckey = GPIO.input(skey)
    key_buf[skey] = ckey

    if pkey== KEY_ON:
        if ckey == KEY_OFF:
            return True
    return False

tms = millis();

while True:
    if (elapsed(tms)) >= 10:
        tms = millis()

        if get_key(KEY1):
            print('KEY1')

        if get_key(KEY2):
            print('KEY2')

        if get_key(KEY3):
            print('KEY3')
        
GPIO.cleanup()   
