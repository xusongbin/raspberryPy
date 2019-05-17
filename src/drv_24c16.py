
# debug done.

import RPi.GPIO as GPIO
from time import time, sleep

# 2k

IO_MODE_OUT = 0
IO_MODE_IN = 1

IO_VAL_HIGH = 1
IO_VAL_LOW = 0

CLK = 5
SDA = 3

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(SDA, GPIO.OUT)

def millis():
    return int(time()*1000)

def elapsed(tms):
    return millis()-tms

def drv_24c16_clk(n):
    if n == IO_VAL_HIGH:
        GPIO.output(CLK, True)
    else:
        GPIO.output(CLK, False)

def drv_24c16_dout(n):
    if n == IO_VAL_HIGH:
        GPIO.output(SDA, True)
    else:
        GPIO.output(SDA, False)

def drv_24c16_din():
    return GPIO.input(SDA)

def drv_24c16_dset(n):
    if n == IO_MODE_OUT:
        GPIO.setup(SDA, GPIO.OUT)
    else:
        GPIO.setup(SDA, GPIO.IN)

def drv_24c16_dus():
    sleep(0.000005)

def drv_24c16_dms():
    sleep(0.005)

def drv_24c16_start():
    drv_24c16_dset(IO_MODE_OUT)
    drv_24c16_clk(IO_VAL_LOW)
    drv_24c16_dout(IO_VAL_HIGH)
    drv_24c16_clk(IO_VAL_HIGH)
    drv_24c16_dus()
    drv_24c16_dout(IO_VAL_LOW)
    drv_24c16_dus()
    drv_24c16_clk(IO_VAL_LOW)
    drv_24c16_dus()
    drv_24c16_dout(IO_VAL_HIGH)

def drv_24c16_stop():
    drv_24c16_dset(IO_MODE_OUT)
    drv_24c16_dout(IO_VAL_LOW)
    drv_24c16_clk(IO_VAL_HIGH)
    drv_24c16_dus()
    drv_24c16_dout(IO_VAL_HIGH)

def drv_24c16_getchar():
    data = 0
    drv_24c16_dset(IO_MODE_OUT)
    drv_24c16_dout(IO_VAL_HIGH)
    drv_24c16_dset(IO_MODE_IN)
    for _ in range(8):
        drv_24c16_clk(IO_VAL_HIGH)
        drv_24c16_dus()
        data <<= 1
        if drv_24c16_din():
            data += 1
        drv_24c16_clk(IO_VAL_LOW)
    drv_24c16_dset(IO_MODE_OUT)
    drv_24c16_dout(IO_VAL_HIGH)
    drv_24c16_clk(IO_VAL_HIGH)
    drv_24c16_dus()
    drv_24c16_clk(IO_VAL_LOW)
    return data

def drv_24c16_putchar(data):
    drv_24c16_dset(IO_MODE_OUT)
    drv_24c16_dout(IO_VAL_HIGH)
    for _ in range(8):
        if data & 0x80:
            drv_24c16_dout(IO_VAL_HIGH)
        else:
            drv_24c16_dout(IO_VAL_LOW)
        data <<= 1
        drv_24c16_clk(IO_VAL_HIGH)
        drv_24c16_dus()
        drv_24c16_clk(IO_VAL_LOW)
    drv_24c16_dout(IO_VAL_LOW)
    drv_24c16_clk(IO_VAL_HIGH)

def drv_24c16_read(addr):
    drv_24c16_start()
    drv_24c16_putchar(0xA0 | ((addr>>8)<<1))
    drv_24c16_dus()
    drv_24c16_clk(IO_VAL_LOW)
    drv_24c16_putchar(addr & 0xFF)
    drv_24c16_dus()
    drv_24c16_clk(IO_VAL_LOW)
    drv_24c16_start()
    drv_24c16_putchar(0xA1)
    drv_24c16_clk(IO_VAL_LOW)
    data = drv_24c16_getchar()
    drv_24c16_stop()
    return data

def drv_24c16_write(addr, data):
    drv_24c16_start()
    drv_24c16_putchar(0xA0 | ((addr>>8)<<1))
    drv_24c16_clk(IO_VAL_LOW)
    drv_24c16_putchar(addr & 0xFF)
    drv_24c16_clk(IO_VAL_LOW)
    drv_24c16_putchar(data)
    drv_24c16_clk(IO_VAL_LOW)
    drv_24c16_stop()
    drv_24c16_dms()

for i in range(2048):
    # drv_24c16_write(i, i)
    if (i % 32) == 0:
        print('')
    print('%02X' % drv_24c16_read(i), end=' ')
print('')

# tms = millis()
# while True:
#     if (elapsed(tms)) >= 1000:
#         tms = millis()

#         pass
            
GPIO.cleanup()

