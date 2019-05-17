
# debug done.

import RPi.GPIO as GPIO
from time import time, sleep

BEEP = 33

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(BEEP, GPIO.OUT)

def millis():
    return int(time()*1000)

def elapsed(tms):
    return millis()-tms

freq = 0;
zkb = 0
pbeep = GPIO.PWM(BEEP, 0.1)
pflag = False

tms = millis()

while True:
    global pbeep
    # if (elapsed(tms)) >= 500:
    #     tms = millis()
    freq = input('Input freq:')
    duty = input('Input duty:')
    try:
        freq = int(freq)
        duty = int(duty)
    except:
        continue
    if pflag is False:
        if freq == 0 or duty == 0:
            pass
        else:
            pbeep.ChangeFrequency(freq)
            pbeep.start(duty)
            pflag = True
    else:
        if freq == 0 or duty == 0:
            pbeep.stop()
            pflag = False
        else:
            pbeep.ChangeDutyCycle(duty)
            pbeep.ChangeFrequency(freq)

GPIO.cleanup()   
