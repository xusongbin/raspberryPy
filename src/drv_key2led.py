
# debug done.

import RPi.GPIO as GPIO
import time


KEY1 = 13
KEY2 = 12
KEY3 = 11

KEY_ON = False
KEY_OFF = True

LED1 = 35
LED2 = 36
LED3 = 32

LED_ON = False
LED_OFF = True

GPIO.setmode(GPIO.BOARD)

GPIO.setup(KEY1, GPIO.IN)
GPIO.setup(KEY2, GPIO.IN)
GPIO.setup(KEY3, GPIO.IN)

GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.setup(LED3, GPIO.OUT)
GPIO.output(LED1, LED_OFF)
GPIO.output(LED2, LED_OFF)
GPIO.output(LED3, LED_OFF)

key_buf = {KEY1:KEY_OFF, KEY2:KEY_OFF, KEY3:KEY_OFF}

def millis():
    return int(time.time()*1000)

def elapsed(tms):
    return millis()-tms

def set_led(led, sta):
    GPIO.output(led, sta)

def reverse_led(led):
    if GPIO.input(led) == LED_ON:
        GPIO.output(led, LED_OFF)
    else:
        GPIO.output(led, LED_ON)

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
            reverse_led(LED1)
            print('KEY1')

        if get_key(KEY2):
            reverse_led(LED2)
            print('KEY2')

        if get_key(KEY3):
            reverse_led(LED3)
            print('KEY3')
        
GPIO.cleanup()   
