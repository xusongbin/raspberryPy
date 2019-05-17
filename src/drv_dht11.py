
# debug done.

import RPi.GPIO as GPIO
from time import time, sleep

DIO = 31

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

def millis():
    return int(time()*1000)

def elapsed(tms):
    return millis()-tms

def micros():
    return int(time()*1000000)

def drv_dht11_output():
    GPIO.setup(DIO, GPIO.OUT)

def drv_dht11_input():
    GPIO.setup(DIO, GPIO.IN)

def drv_dht11_write(val):
    if val:
        GPIO.output(DIO, True)
    else:
        GPIO.output(DIO, False)

def drv_dht11_read():
    return GPIO.input(DIO)

def drv_dht11_release():
    drv_dht11_output()
    drv_dht11_write(True)

def drv_dht11_get():
    buf = [0, 0, 0, 0, 0]
    ret = [0, 0, 0]
    val = 0
    tus = 0
    i = 0

    drv_dht11_output()
    drv_dht11_write(0)
    sleep(0.03)
    drv_dht11_write(1)
    drv_dht11_input()

    tus = micros()
    while not drv_dht11_read():
        if (micros() - tus) > 120:
            print("ack time out")
            drv_dht11_release()
            ret[0] = -1
            return ret
    
    tus = micros()
    while drv_dht11_read():
        if (micros() - tus) > 120:
            print("notice time out")
            drv_dht11_release()
            ret[0] = -2
            return ret

    for i in range(40):
        if (i % 8) == 0:
            val = 0
        
        tus = micros();
        while not drv_dht11_read():
            if (micros() - tus) > 50:
                print("read data wait high err,i=%d" % i)
                drv_dht11_release()
                ret[0] = -3
                return ret

        tus = micros();
        while drv_dht11_read():
            if (micros() - tus) > 70:
                print("read data wait low err,i=%d" % i)
                drv_dht11_release()
                ret[0] = -4
                return ret
        
        val <<= 1
        if (micros() - tus) > 35:
            val += 1 
        
        buf[int(i/8)] = val;
    
    drv_dht11_release()

    val = (buf[0] + buf[1] + buf[2] + buf[3]) & 0xFF
    if val ==  buf[4]:
        ret[1] = buf[0]
        ret[2] = buf[2]
        return ret
    else:
        print("check sum err!%x-%x" % (val, buf[4]))
        ret[0] = -5
        return ret

tms = millis()

while True:
    if (elapsed(tms)) >= 2000:
        tms = millis()

        err, humy, temp = drv_dht11_get()
        if err < 0:
            pass
        else:
            print('current=>temp:%d humy:%d' % (temp, humy))
            
GPIO.cleanup()

