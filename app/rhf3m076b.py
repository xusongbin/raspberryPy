#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from time import time, sleep

import serial
from serial.tools import list_ports


from my_driver import *


def main():
    ser = MySerial('VID:PID=0483:5740', 115200, 200)
    print(ser.set_reopen())
    if ser.set_send('AT', '+'):
        print(ser.get_receive_str())
    if ser.set_send('AT+MODE=TEST', '+'):
        print(ser.get_receive_str())
    if ser.set_send('AT+TEST=TXCW', '+'):
        print(ser.get_receive_str())


if __name__ == "__main__":
    main()
