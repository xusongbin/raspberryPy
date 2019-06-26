#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import RPi.GPIO as GPIO
from spidev import SpiDev
from time import time, sleep


RST = 22
CS0 = 24

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(RST, GPIO.OUT)
GPIO.setup(CS0, GPIO.OUT)

spi = SpiDev()
spi.open(0, 0)

def millis():
    return int(time()*1000)

def elapsed(tms):
    return millis()-tms

tms = millis()

def gpio_ctl(pin, val):
    GPIO.output(pin, val)

def spi_init():
    spi.max_speed_hz = 8000000
    spi.no_cs = True
    spi.mode = 0
    gpio_ctl(RST, False)
    sleep(0.01)
    gpio_ctl(RST, True)
    sleep(0.5)

def lgw_spi_w(addr, data):
    gpio_ctl(CS0, False)
    spi.xfer([addr | 0x80])
    spi.xfer([data])
    gpio_ctl(CS0, True)
    return True

def lgw_spi_r(addr):
    gpio_ctl(CS0, False)
    spi.xfer([addr & 0x7F])
    data = spi.xfer([0x00])[0]
    gpio_ctl(CS0, True)
    return data

def lgw_spi_wb(addr, buf, size):
    gpio_ctl(CS0, False)
    spi.xfer([addr | 0x80])
    for i in range(size):
        spi.xfer([buf[i]])
    gpio_ctl(CS0, True)
    return True

def lgw_spi_rb(addr, size):
    buf = []
    gpio_ctl(CS0, False)
    spi.xfer([addr & 0x7F])
    for _ in range(size):
        buf.append(spi.xfer([0x00]))
    gpio_ctl(CS0, True)
    return buf

if __name__ == "__main__":
    spi_init()
    print(lgw_spi_r(int(sys.argv[1])))
