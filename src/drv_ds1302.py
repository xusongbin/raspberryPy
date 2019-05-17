
# debug done.

import RPi.GPIO as GPIO
from time import time, sleep

DS1302_SECOND_W = 0x80
DS1302_SECOND_R = 0x81
DS1302_MINUTE_W = 0x82
DS1302_MINUTE_R = 0x83
DS1302_HOUR_W = 0x84
DS1302_HOUR_R = 0x85
DS1302_DATE_W = 0x86
DS1302_DATE_R = 0x87
DS1302_MONTH_W = 0x88
DS1302_MONTH_R = 0x89
DS1302_WEEK_W = 0x8A
DS1302_WEEK_R = 0x8B
DS1302_YEAR_W = 0x8C
DS1302_YEAR_R = 0x8D
DS1302_PROTECT_W = 0x8E
DS1302_PROTECT_R = 0x8F

IO_MODE_OUT = 0
IO_MODE_IN = 1

IO_VAL_HIGH = 1
IO_VAL_LOW = 0

CLK = 15
DIO = 16
RST = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(RST, GPIO.OUT)
GPIO.setup(DIO, GPIO.OUT)

def millis():
    return int(time()*1000)

def elapsed(tms):
    return millis()-tms

tms = millis()

def uchar_to_bcd(n):
    return (((n / 10) << 4) | (n % 10))

def bcd_to_uchar(n):
    return ((n >> 4) * 10 + (n & 0xF))

def drv_ds1302_clk(n):
    if n == IO_VAL_HIGH:
        GPIO.output(CLK, True)
    else:
        GPIO.output(CLK, False)

def drv_ds1302_rst(n):
    if n == IO_VAL_HIGH:
        GPIO.output(RST, True)
    else:
        GPIO.output(RST, False)

def drv_ds1302_dout(n):
    if n == IO_VAL_HIGH:
        GPIO.output(DIO, True)
    else:
        GPIO.output(DIO, False)

def drv_ds1302_dset(n):
    if n == IO_MODE_OUT:
        GPIO.setup(DIO, GPIO.OUT)
    else:
        GPIO.setup(DIO, GPIO.IN)

def drv_ds1302_din():
    return GPIO.input(DIO)

def drv_ds1302_delay():
    sleep(0.000005)

def drv_ds1302_putchar(data):
    drv_ds1302_dset(IO_MODE_OUT)
    drv_ds1302_delay()
    for _ in range(8):
        if data & 0x01:
            drv_ds1302_dout(IO_VAL_HIGH)
        else:
            drv_ds1302_dout(IO_VAL_LOW)
        drv_ds1302_clk(IO_VAL_HIGH)
        drv_ds1302_delay()
        drv_ds1302_clk(IO_VAL_LOW)
        drv_ds1302_delay()
        data >>= 1
def drv_ds1302_getchar():
    data = 0
    drv_ds1302_dset(IO_MODE_IN)
    drv_ds1302_delay()
    for _ in range(8):
        data >>= 1
        if drv_ds1302_din():
            data |= 0x80;
        drv_ds1302_clk(IO_VAL_HIGH)
        drv_ds1302_delay()
        drv_ds1302_clk(IO_VAL_LOW)
        drv_ds1302_delay()
    return data

def drv_ds1302_write_addr(addr, data):
    drv_ds1302_rst(IO_VAL_LOW)
    drv_ds1302_clk(IO_VAL_LOW)
    drv_ds1302_rst(IO_VAL_HIGH)
    drv_ds1302_putchar(addr)
    drv_ds1302_putchar(data)
    drv_ds1302_rst(IO_VAL_LOW)
    drv_ds1302_clk(IO_VAL_HIGH)

def drv_ds1302_read_addr(addr):
    drv_ds1302_rst(IO_VAL_LOW)
    drv_ds1302_clk(IO_VAL_LOW)
    drv_ds1302_rst(IO_VAL_HIGH)
    drv_ds1302_putchar(addr)
    data = drv_ds1302_getchar()
    drv_ds1302_clk(IO_VAL_HIGH)
    drv_ds1302_rst(IO_VAL_LOW)
    return data

def drv_ds1302_time_write(tt):
    drv_ds1302_write_addr(DS1302_PROTECT_W, 0x00)
    drv_ds1302_write_addr(DS1302_YEAR_W, uchar_to_bcd(tt['year']))
    drv_ds1302_write_addr(DS1302_MONTH_W, uchar_to_bcd(tt['month']))
    drv_ds1302_write_addr(DS1302_DATE_W, uchar_to_bcd(tt['date']))
    drv_ds1302_write_addr(DS1302_WEEK_W, uchar_to_bcd(tt['week']))
    drv_ds1302_write_addr(DS1302_HOUR_W, uchar_to_bcd(tt['hour']))
    drv_ds1302_write_addr(DS1302_MINUTE_W, uchar_to_bcd(tt['minute']))
    drv_ds1302_write_addr(DS1302_SECOND_W, uchar_to_bcd(tt['second']))
    drv_ds1302_write_addr(DS1302_PROTECT_W, 0x80)

def drv_ds1302_time_read():
    tt = {}
    tt['year'] = bcd_to_uchar(drv_ds1302_read_addr(DS1302_YEAR_R))
    tt['month'] = bcd_to_uchar(drv_ds1302_read_addr(DS1302_MONTH_R))
    tt['date'] = bcd_to_uchar(drv_ds1302_read_addr(DS1302_DATE_R))
    tt['week'] = bcd_to_uchar(drv_ds1302_read_addr(DS1302_WEEK_R))
    tt['hour'] = bcd_to_uchar(drv_ds1302_read_addr(DS1302_HOUR_R))
    tt['minute'] = bcd_to_uchar(drv_ds1302_read_addr(DS1302_MINUTE_R))
    tt['second'] = bcd_to_uchar(drv_ds1302_read_addr(DS1302_SECOND_R))
    return tt

def app_ds1302_evt():
    tt = drv_ds1302_time_read()
    _str = 'DS1302=>%02d-%02d-%02d' % (tt['year'], tt['month'], tt['date'])
    _str += ' %02d:%02d:%02d %d' % (tt['hour'], tt['minute'], tt['second'], tt['week'])
    print(_str)

while True:
    if (elapsed(tms)) >= 1000:
        tms = millis()

        app_ds1302_evt()
            
GPIO.cleanup()

