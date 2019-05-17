
# debug done.

import RPi.GPIO as GPIO
from time import time, sleep

TRIG = 38
ECHO = 40

GPIO.setmode(GPIO.BOARD)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(TRIG, GPIO.OUT)

def millis():
    return int(time()*1000)

def elapsed(tms):
    return millis()-tms

tms = millis()

while True:
    if (elapsed(tms)) >= 1000:
        tms = millis()


        GPIO.output(TRIG, True)
        sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO) == 0:
            pass
        timer_start = time()

        while GPIO.input(ECHO) == 1:
            if (time() - timer_start) > 0.0235:
                break
        timer_stop = time()

        timer_cm = (timer_stop - timer_start) * 1000000
        if 115 < timer_cm < 23500:
            distance = int(timer_cm / 58)
            print('Current distance=%dcm' % distance)
            
GPIO.cleanup()

