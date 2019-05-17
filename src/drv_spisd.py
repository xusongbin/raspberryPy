
# debug done.

from spidev import SpiDev
from time import time, sleep

HAL_OK = 0
HAL_ERR = 1
HAL_ERR1 = 2
# SD card type define
SD_TYPE_ERR = 0x00
SD_TYPE_MMC = 0x01
SD_TYPE_V1 = 0X02
SD_TYPE_V2 = 0X04
SD_TYPE_V2HC = 0X06
# SD card command table
CMD0 = 0    # card reset
CMD1 = 1
CMD8 = 8    # SEND_IF_COND
CMD9 = 9    # read CSD data
CMD10 = 10  # read CID data
CMD12 = 12  # stop data transfer
CMD16 = 16  # set SectoeSize return 0x00
CMD17 = 17  # read sector
CMD18 = 18  # read Multi sector
CMD23 = 23  # erase N block before sett Multi sector
CMD24 = 24  # write sector
CMD25 = 25  # write Multi sector
CMD41 = 41  # return 0x00
CMD55 = 55  # return 0x01
CMD58 = 58  # read OCR info
CMD59 = 59  # Enable/Disable CRC need return 0x00
# data write resport
MSD_DATA_OK = 0x05
MSD_DATA_CRC_ERROR = 0x0B
MSD_DATA_WRITE_ERROR = 0x0D
MSD_DATA_OTHER_ERROR = 0xFF
# SD card resport
MSD_RESPONSE_NO_ERROR = 0x00
MSD_IN_IDLE_STATE = 0x01
MSD_ERASE_RESET = 0x02
MSD_ILLEGAL_COMMAND = 0x04
MSD_COM_CRC_ERROR = 0x08
MSD_ERASE_SEQUENCE_ERROR = 0x10
MSD_ADDRESS_ERROR = 0x20
MSD_PARAMETER_ERROR = 0x40
MSD_RESPONSE_FAILURE = 0xFF

def millis():
    return int(time()*1000)

def elapsed(tms):
    return millis()-tms

spi = SpiDev()
spi.open(0, 0)

sd_type = SD_TYPE_ERR

tms = millis()

# spi write and read a byte
def spi_readwrite_byte(n):
    n &= 0xFF
    return spi.xfer([n])[0]

def spi_read_buf(n):
    return spi.xfer([0xFF for _ in range(n)])

def spi_write_buf(buf):
    spi.xfer(buf)

def spi_read_cmp(res, num):
    for _ in range(num):
        cres = spi_readwrite_byte(0xFF)
        if cres == res:
            return HAL_OK
    return HAL_ERR

# set spi data rate, initialization rate is no more than 400k
def spi_set_speed(n):
    spi.max_speed_hz = n

# Release SPI Bus by Canceling Chip Selection
def sd_disselect():
    # CS_H
    spi_readwrite_byte(0xFF)

# Wait for card ready
def sd_waitready():
    return spi_read_cmp(0xFF, 0xFFFFFF)

# select sd card and wait for ready
# 0:OK  1:ERR
def sd_select():
    # CS_L
    if sd_waitready() == HAL_OK:
        return HAL_OK
    sd_disselect()
    return HAL_ERR

# get response is res or not
def sd_get_response(res):
    if spi_read_cmp(res, 0xFFFF) == HAL_OK:
        return MSD_RESPONSE_NO_ERROR
    return MSD_RESPONSE_FAILURE

# read a length of data from sd card
def sd_recvdata(plen):
    if sd_get_response(0xFE):
        return HAL_ERR, []
    buf = spi_read_buf(plen)
    spi_readwrite_byte(0xFF)
    spi_readwrite_byte(0xFF)
    return HAL_OK, buf

# write a block data to sd card
def sd_sendblock(buf, cmd):
    if sd_waitready():
        return HAL_ERR
    if cmd != 0xFD:
        spi_write_buf(buf)
        spi_readwrite_byte(0xFF)
        spi_readwrite_byte(0xFF)
        t = spi_readwrite_byte(0xFF)
        if (t & 0x1F) != 0x05:
            return HAL_ERR1
    return HAL_OK

# send a command to sd card
def sd_sendcmd(cmd, arg, crc):
    sd_disselect()
    if sd_select():
        return 0xFF
    spi_readwrite_byte(cmd | 0x40)
    spi_readwrite_byte(arg >> 24)
    spi_readwrite_byte(arg >> 16)
    spi_readwrite_byte(arg >> 8)
    spi_readwrite_byte(arg)
    spi_readwrite_byte(crc)
    if cmd == CMD12:    # Skip a stuff byte when stop reading
        spi_readwrite_byte(0xFF)
    for _ in range(0x1F):
        r1 = spi_readwrite_byte(0xFF)
        if (r1 & 0x80) != 0x80:
            break
    return r1

# get sd card CID info, include manufacturer info
def sd_get_cid():
    if sd_sendcmd(CMD10, 0, 0x01) == 0x00:
        return  sd_recvdata(16)
    return HAL_ERR, []

# get sd card CSD info, include capacity and speed
def sd_get_csd():
    if sd_sendcmd(CMD9, 0, 0x01) == 0x00:
        return sd_recvdata(16)
    return HAL_ERR, []

# get sd card total sector number
def sd_get_sectorcount():
    err, csd = sd_get_csd()
    if err != HAL_OK:
        return 0
    if (csd[0] & 0xC0) == 0x40:     # V2.00 card
        csize = csd[9] + csd[8] << 8 + 1
        capacity = csize << 10
    else:       # V1.xx card
        n = (csd[5] & 15) + (csd[10] & 128) >> 7 + (csd[9] & 3) << 1 + 2
        csize = csd[8] >> 6 + csd[7] << 2 + (csd[6] & 3) << 10 + 1
        capacity = csize << (n - 9)
    return capacity

# initialization SD card
def sd_init_config():
    global sd_type

    spi_set_speed(400000)
    print('debug->set spi speed to 400k')
    spi_write_buf([0xFF for _ in range(10)])
    print('debug->write 10 byte 0xFF to sd')
    for _ in range(20):
        r1 = sd_sendcmd(CMD0, 0, 0x95)
        if r1 == 0x01:
            break
    sd_type = SD_TYPE_ERR     # default not card
    print('debug->start get sd type, r1:%d' % r1)
    if r1 == 0x01:
        if sd_sendcmd(CMD8, 0x1AA, 0x87) == 1:      # sd v2.0
            print('debug->get sd is v2.0')
            buf = spi_read_buf(4)   # Get trailing return value of R7 resp
            if (buf[2] == 0x01) and (buf[3] == 0xAA):    # check card support 2.7~3.6V or not
                print('debug->check card support 2.7~3.6V or not')
                retry = 0xFFFE
                while retry:
                    sd_sendcmd(CMD55, 0, 0x01)      # send CMD55
                    if sd_sendcmd(0x41, 0x40000000, 0x01) == 0: # send CMD41
                        break
                    retry -= 1
                if retry and sd_sendcmd(CMD58, 0, 0x01) == 0:     # start check SD2.0
                    buf = spi_read_buf(4)   # get OCR
                    if buf[0] & 0x40:       # check CCS
                        print('debug->check card type V2HC')
                        sd_type = SD_TYPE_V2HC
                    else:
                        print('debug->check card type V2')
                        sd_type = SD_TYPE_V2
            else:   # SD V1.x  MMC  V3
                print('debug->check card type V1.x MMC V3')
                sd_sendcmd(CMD55, 0, 0x01)  # send CMD55
                r1 = sd_sendcmd(CMD41, 0, 0x01) # send CMD41
                if r1 <= 1:
                    print('debug->check card type V1')
                    sd_type = SD_TYPE_V1
                    retry = 0xFFFE
                    while retry:
                        sd_sendcmd(CMD55, 0, 0x01)  # send CMD55
                        r1 = sd_sendcmd(CMD41, 0, 0x01) # send CMD41
                        if r1 == 0:
                            break
                        retry -= 1
                else:
                    print('debug->check card type MMC')
                    sd_type = SD_TYPE_MMC
                    retry = 0xFFFE
                    while retry:
                        r1 = sd_sendcmd(CMD1, 0, 0x01)
                        if r1 == 0:
                            break
                        retry -= 1
                if retry == 0 or sd_sendcmd(CMD16, 512, 0x01) != 0:
                    print('debug->check card type ERR')
                    sd_type = SD_TYPE_ERR
    sd_disselect()
    spi_set_speed(52000000)
    print('debug->set spi speed to 52M')
    if sd_type:
        return HAL_OK
    elif r1:
        return r1
    return 0xAA

def sd_read_disk2(sector, cnt):
    if sd_type != SD_TYPE_V2HC:
        sector <<= 9
    buf = []
    if cnt == 1:
        r1 = sd_sendcmd(CMD17, sector, 0x01)
        if r1 == 0:
            r1, buf = sd_recvdata(512)
    else:
        r1 = sd_sendcmd(CMD18, sector, 0x01)
        while cnt:
            r1, tbuf = sd_recvdata(512)
            buf += tbuf
            if r1 != HAL_OK:
                break
            cnt -= 1
        sd_sendcmd(CMD12, 0, 0X01)
    sd_disselect()
    return r1, buf

def sd_write_disk2(buf, sector, cnt):
    if sd_type != SD_TYPE_V2HC:
        sector *= 512
    if cnt == 1:
        r1 = sd_sendcmd(CMD24, sector, 0x01)
        if r1 == 0:
            r1 = sd_sendblock(buf, 0xFE)
    else:
        if sd_type == SD_TYPE_MMC:
            sd_sendcmd(CMD55, 0, 0x01)
            sd_sendcmd(CMD23, cnt, 0x01)
        r1 = sd_sendcmd(CMD25, sector, 0x01)
        if r1 == 0:
            while cnt:
                r1 = sd_sendblock(buf, 0xFC)
                buf = buf[512:]
                if r1 != 0:
                    break
                cnt -= 1
            r1 = sd_sendblock(0, 0xFD)
    sd_disselect()
    return r1

if sd_init_config() == HAL_OK:
    print('debug->get capacity:%d' % sd_get_sectorcount())
    err, buf = sd_read_disk2(0, 1)
    if err == HAL_OK:
        print('debug->get block:')
        buf = [hex(i)[2:].rjust(2, '0').upper() for i in buf]
        for i, d in enumerate(buf):
            if i%32==0 and i != 0:
                print()
            print(d, end=' ')
        print()
    else:
        print('debug->get block err')

# while True:
#     if (elapsed(tms)) >= 1000:
#         tms = millis()

