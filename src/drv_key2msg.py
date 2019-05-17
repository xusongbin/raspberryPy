
# debug done.

import RPi.GPIO as GPIO
from time import time, sleep

RCLK = 37
SCLK = 38
DIO = 40

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

num_buf = [0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x6F,0x77,0x7C,0x39,0x5E,0x79,0x71,0xFF]
# ctl_buf = [0xFF, 0xFE, 0xFD, 0xFB, 0xF7]
ctl_buf = [0xFF, 0xF7, 0xFB, 0xFD, 0xFE]

key_buf = {KEY1:KEY_OFF, KEY2:KEY_OFF, KEY3:KEY_OFF}

GPIO.setmode(GPIO.BOARD)

GPIO.setup(RCLK, GPIO.OUT)
GPIO.setup(SCLK, GPIO.OUT)
GPIO.setup(DIO, GPIO.OUT)

GPIO.setup(KEY1, GPIO.IN)
GPIO.setup(KEY2, GPIO.IN)
GPIO.setup(KEY3, GPIO.IN)

GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.setup(LED3, GPIO.OUT)

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

tick = millis();
tms = millis();

data = 0
while True:
    if (elapsed(tick)) >= 10:
        tick = millis()
        
        if get_key(KEY1):
            reverse_led(LED1)
            data += 1
        
        if get_key(KEY2):
            reverse_led(LED2)
            data += 10
        
        if get_key(KEY3):
            reverse_led(LED3)
            data += 100

    set_str(data)
        
GPIO.cleanup()   
