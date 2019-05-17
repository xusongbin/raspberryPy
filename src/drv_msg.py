
# debug done.

import RPi.GPIO as GPIO
from time import time, sleep

RCLK = 37
SCLK = 38
DIO = 40

num_buf = [0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x6F,0x77,0x7C,0x39,0x5E,0x79,0x71,0xFF]
# ctl_buf = [0xFF, 0xFE, 0xFD, 0xFB, 0xF7]
ctl_buf = [0xFF, 0xF7, 0xFB, 0xFD, 0xFE]

GPIO.setmode(GPIO.BOARD)

GPIO.setup(RCLK, GPIO.OUT)
GPIO.setup(SCLK, GPIO.OUT)
GPIO.setup(DIO, GPIO.OUT)

def millis():
    return int(time()*1000)

def elapsed(tms):
    return millis()-tms

def set_char(data):
    bit = 0x80
    for _ in range(8):
        GPIO.output(SCLK, False)
        if data & bit:
            GPIO.output(DIO, True)
        else:
            GPIO.output(DIO, False)
        GPIO.output(SCLK, True)
        bit = int(bit/2)

def set_data(data, ctl):
    GPIO.output(RCLK, False)
    set_char(data);
    set_char(ctl);
    GPIO.output(RCLK, True)

def set_str(data):
    num1 = int(data / 1) % 10
    num2 = int(data / 10) % 10
    num3 = int(data / 100) % 10
    num4 = int(data / 1000) % 10

    set_data(num_buf[num1], ctl_buf[1])
    set_data(num_buf[num2], ctl_buf[2])
    set_data(num_buf[num3], ctl_buf[3])
    set_data(num_buf[num4], ctl_buf[4])
    set_data(num_buf[10], ctl_buf[0])

tick = millis();
tms = millis();

data = 0
while True:
    if (elapsed(tick)) >= 50:
        tick = millis()
        data += 1

    set_str(data)
        
GPIO.cleanup()   
