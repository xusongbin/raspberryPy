
# debug done.

import smbus
from time import time, sleep

# 2k

bus = smbus.SMBus(1)

def millis():
    return int(time()*1000)

def elapsed(tms):
    return millis()-tms

def drv_24c16_read(addr):
    data = bus.read_byte_data(0x50 | addr>>8, addr&0xFF)
    # print('read data:', data)
    return data


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
            
bus.close()

