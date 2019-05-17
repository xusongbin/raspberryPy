
# debug done.

import RPi.GPIO as GPIO
from time import time, sleep


LED1 = 35
LED2 = 36
LED3 = 32

LED_ON = False
LED_OFF = True

GPIO.setmode(GPIO.BOARD)

GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.setup(LED3, GPIO.OUT)

def millis():
    return int(time()*1000)

def elapsed(tms):
    return millis()-tms

tms = millis()
cnt = 0;

while True:
    if (elapsed(tms)) >= 1000:
        tms = millis()
        cnt += 1

        if cnt & 0x01:
            GPIO.output(LED1, LED_ON)
        else:
            GPIO.output(LED1, LED_OFF)

        if cnt & 0x02:
            GPIO.output(LED2, LED_ON)
        else:
            GPIO.output(LED2, LED_OFF)

        if cnt & 0x04:
            GPIO.output(LED3, LED_ON)
        else:
            GPIO.output(LED3, LED_OFF)
        
GPIO.cleanup()   
