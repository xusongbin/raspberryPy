
# 

import serial
from time import time, sleep

ser = serial.Serial(
    port = '/dev/ttyAMA0',
    #port = '/dev/usb',
    baudrate = 115200,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1
)

while True:
    rx = ser.readline()
    if rx:
        print('Uart RX:', rx.decode())
        ser.write(rx)
    sleep(0.01);