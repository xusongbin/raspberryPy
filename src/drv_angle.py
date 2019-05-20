
# debug done.
# 倾斜/角度传感器

import RPi.GPIO as GPIO
import time


SENSOR_PIN = 11

SENSOR_LOW = False
SENSOR_HIGH = True

GPIO.setmode(GPIO.BOARD)    # Physical

GPIO.setup(SENSOR_PIN, GPIO.IN)

def millis():
    return int(time.time()*1000)

def elapsed(tms):
    return millis()-tms

def get_sensor():
    return GPIO.input(SENSOR_PIN)

tms = millis();

last_sta = SENSOR_LOW

if __name__ == "__main__":
    global last_sta
    while True:
        if (elapsed(tms)) >= 50:
            tms = millis()

            sta = get_sensor()
            if sta != last_sta:
                last_sta = sta
                
                print('{:<15}angle {}.'.format(millis(), 'HIGH' if sta else 'LOW'))
        
GPIO.cleanup()   
