#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import queue
import sqlite3
import threading
from time import time, sleep, strftime, localtime
import socket

import xlwt
import xlrd
import shutil
import serial
from serial.tools import list_ports


def write_log(_str):
    _data = strftime("%Y-%m-%d %H:%M:%S", localtime())
    _data += '.%03d ' % (int(time() * 1000) % 1000)
    _data += _str
    try:
        print(_data)
        with open('log.txt', 'a+') as f:
            f.write(_data + '\n')
    except Exception as e:
        print('write log exception %s' % e)


class MyFile(object):
    def __init__(self, log=True):
        self.log = log

    def create(self, file):
        try:
            if '/' in file:
                if not os.path.isdir(file[0:file.rfind('/') + 1]):
                    os.makedirs(file[0:file.rfind('/') + 1])
            f = open(file, 'w')
            f.close()
        except Exception as e:
            if self.log:
                write_log('File create exception: %s' % e)
            return False
        return True

    def delete(self, file):
        try:
            if os.path.exists(file) is True:
                os.remove(file)
        except Exception as e:
            if self.log:
                write_log('File delete exception: %s' % e)
            return False
        return True

    def copy(self, src, des):
        if self.access(des):
            if not self.delete(des):
                if self.log:
                    write_log('File copy exception: Target file exists.')
                return False
        try:
            shutil.copyfile(src, des)
            return True
        except Exception as e:
            if self.log:
                write_log('File copy exception: %s' % e)
            return False

    def access(self, file):
        try:
            return os.path.exists(file)
        except Exception as e:
            if self.log:
                write_log('File access exception: %s' % e)
            return False

    def get_size(self, file):
        try:
            return os.path.getsize(file)
        except Exception as e:
            if self.log:
                write_log('File get_size exception: %s' % e)
            return -1

    def write(self, file, data, mode='string'):
        # 'string' or 'byte'
        try:
            if not self.create(file):
                return False
            if mode == 'string':
                f = open(file, 'w')
            else:
                f = open(file, 'wb')
            f.write(data)
            f.close()
        except Exception as e:
            if self.log:
                write_log('File write exception: %s' % e)
            return False
        return True

    def read(self, file, mode='string'):
        # 'string' or 'byte'
        try:
            if not self.access(file):
                return False
            if mode == 'string':
                f = open(file, 'r')
            else:
                f = open(file, 'rb')
            _data = f.read()
            f.close()
        except Exception as e:
            if self.log:
                write_log('File read exception: %s' % e)
            return False
        return _data


class MySerial(object):
    def __init__(self, hid, baud, timeout, com='', log=True, wakeup=False, enter=True):
        self.serial_baud = baud
        self.serial_byte = 8
        self.serial_parity = serial.PARITY_NONE
        self.serial_stopbits = 1

        self.serial_hid = hid
        self.serial_com = com
        self.serial_port = serial.Serial()
        self.timeout = timeout

        self.receive = ''
        self.buffer = ''
        self.open = False
        self.log = log
        self.wakeup = wakeup
        self.enter = enter
        self.name = ''
        if not com == '':
            self.name = com
        self.rx_qq = queue.Queue()

    def set_timeout(self, ts):
        self.timeout = ts

    def cls_rx_qq(self):
        self.rx_qq.queue.clear()

    def get_valid(self):
        return self.open

    def get_com_list(self):
        _list = []
        try:
            for _describe in list_ports.comports():
                _list.append(str(_describe).split('-')[0].strip())
        except Exception as e:
            if self.log:
                write_log('Serial get com list exception:%s' % e)
        return _list

    def get_com_by_hid(self, hid=''):
        if hid == '':
            hid = self.serial_hid
        try:
            for _describe in list_ports.comports():
                if hid in _describe.hwid:
                    return str(_describe).split('-')[0].strip()
        except Exception as e:
            if self.log:
                write_log('Serial get com by hid exception:%s' % e)
        return ''

    def get_receive_str(self):
        return self.receive

    def get_receive_line(self):
        self.receive += '\n'
        return self.receive.split('\n')[0].strip()

    def set_close(self):
        self.open = False
        try:
            self.serial_port.close()
        except Exception as e:
            if self.log:
                write_log('Serial close exception: %s' % e)

    def set_open(self):
        try:
            self.serial_port = serial.Serial(
                port=self.name,
                baudrate=self.serial_baud,
                bytesize=self.serial_byte,
                stopbits=self.serial_stopbits,
                parity=self.serial_parity,
                timeout=0)
            if self.log:
                write_log('Serial open successful %s' % self.name)
            self.open = True
            return True
        except Exception as e:
            if self.log:
                write_log('Serial open exception %s %s' % (self.name, e))
            return False

    def set_reopen(self):
        self.set_close()
        if self.serial_com == '':
            self.name = self.get_com_by_hid()
        else:
            self.name = self.serial_com
        if self.name == '':
            return False
        return self.set_open()

    def set_send(self, tx, rx, wait=True):
        self.receive = ''
        self.buffer = ''
        if tx != '':
            if self.enter:
                tx = str(tx).strip() + '\r\n'
            try:
                if self.wakeup:
                    self.serial_port.write(b'\xff\xff\xff\xff')
                self.serial_port.write(tx.encode('utf-8'))
                write_log('Serial tx %s:%s' % (self.name, tx))
            except Exception as e:
                if self.log:
                    write_log('Serial tx exception %s' % e)
                self.set_reopen()
                if self.open is True:
                    self.serial_port.write(tx.encode('utf-8'))
                else:
                    return False

        if not wait:
            return True

        _start = int(round(time() * 1000))
        _now = int(round(time() * 1000))
        while _now - _start < self.timeout:
            line = ''
            try:
                if self.serial_port.inWaiting() > 0:
                    line = self.serial_port.readline()
            except Exception as e:
                if self.log:
                    write_log('receive serial exception %s' % e)
                self.set_reopen()
                if self.open is False:
                    return False
            if line != '':
                self.buffer += line.decode("utf-8", "ignore")
                _start = int(round(time() * 1000))
            _now = int(round(time() * 1000))
            sleep(0.01)
        if self.buffer != '':
            write_log('Serial rx %s:%s' % (self.name, self.buffer))
            for dd in self.buffer.split('\n'):
                self.rx_qq.put(dd.strip())
        if rx == '':
            self.receive = self.buffer
            return True
        elif self.buffer != '' and rx in self.buffer:
            self.receive = self.buffer[self.buffer.rfind(rx):]
            return True
        return False


class MySerialThread(object):
    def __init__(
            self,
            baud=115200,
            byte=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
            com='', hid='',
            log=True, wakeup=False, enter=True, clear=True):
        self.serial_baud = baud
        self.serial_byte = byte
        self.serial_parity = parity
        self.serial_stopbits = stopbits
        self.serial_port = serial.Serial()

        self.serial_hid = hid
        self.serial_com = com

        self.log = log
        self.wakeup = wakeup
        self.enter = enter
        self.clear = clear
        self.open = False

        self.tx_qq = queue.Queue()
        self.rx_qq = queue.Queue()

        self.thread_flag = True
        self.thread_tx = threading.Thread(target=self.thread_tx_event)
        self.thread_tx.setDaemon(True)
        self.thread_tx.start()
        self.thread_rx = threading.Thread(target=self.thread_rx_event)
        self.thread_rx.setDaemon(True)
        self.thread_rx.start()

    def get_com_list(self):
        _list = []
        try:
            for _describe in list_ports.comports():
                _list.append(str(_describe).split('-')[0].strip())
        except Exception as e:
            if self.log:
                write_log('Serial get com list exception:%s' % e)
        return _list

    def get_com_by_hid(self, hid=''):
        if hid == '':
            hid = self.serial_hid
        try:
            for _describe in list_ports.comports():
                if hid in _describe.hwid:
                    return str(_describe).split('-')[0].strip()
        except Exception as e:
            if self.log:
                write_log('Serial get com by hid exception:%s' % e)
        return ''

    def set_close(self):
        self.open = False
        try:
            self.serial_port.close()
        except Exception as e:
            if self.log:
                write_log('Serial close exception: %s' % e)

    def set_open(self, mode='COM'):
        if mode == 'HID':
            com = self.get_com_by_hid()
        else:
            com = self.serial_com
        try:
            self.serial_port = serial.Serial(
                port=com,
                baudrate=self.serial_baud,
                bytesize=self.serial_byte,
                stopbits=self.serial_stopbits,
                parity=self.serial_parity,
                timeout=0)
            if self.log:
                write_log('Serial open successful: %s' % com)
            self.open = True
            if self.clear:
                self.set_clear()
            return True
        except Exception as e:
            if self.log:
                write_log('Serial open exception: %s' % e)
        return False

    def set_clear(self):
        self.tx_qq.queue.clear()
        self.rx_qq.queue.clear()

    def set_send(self, tx):
        self.tx_qq.put(tx)

    def get_receive(self):
        if not self.rx_qq.empty():
            return self.rx_qq.get()
        return False

    def thread_tx_event(self):
        while self.serial_hid:
            if self.open and not self.tx_qq.empty():
                tx = self.tx_qq.get()
                if self.enter:
                    tx = str(tx).strip() + '\r\n'
                try:
                    if self.wakeup:
                        self.serial_port.write(b'\xff\xff\xff\xff')
                    self.serial_port.write(tx.encode('utf-8'))
                    if self.log:
                        write_log('Serial tx %s:%s' % (self.serial_port.name, tx))
                except Exception as e:
                    self.set_close()
                    if self.log:
                        write_log('Serial tx exception: %s' % e)

    def thread_rx_event(self):
        while self.serial_hid:
            if not self.open:
                if self.serial_hid != '':
                    self.set_open('HID')
                else:
                    self.set_open()
                continue
            else:
                try:
                    if self.serial_port.inWaiting() > 0:
                        _data = self.serial_port.readline().decode("utf-8", "ignore")
                        self.rx_qq.put(_data)
                        if self.log:
                            write_log('Serial rx %s:%s' % (self.serial_port.name, _data))
                except Exception as e:
                    self.set_close()
                    if self.log:
                        write_log('Serial rx exception: %s' % e)


class MySQLite3(object):
    def __init__(self, db='', log=True):
        self.db = db
        self.log = log
        self.conn = sqlite3.connect(self.db, check_same_thread=False)

    def set_database(self, db):
        if self.db != db:
            self.db = db
            self.conn.close()
            self.conn = sqlite3.connect(self.db)

    def set_close(self):
        self.conn.close()

    def get_table(self, name):
        try:
            data = self.conn.cursor().execute(
                'select COUNT(*) from sqlite_master where type=\'table\' and name=\'{}\''.format(name)).fetchall()
            if data[0][0] == 1:
                return True
            return False
        except Exception as e:
            if self.log:
                write_log('search table failure:%s' % e)
            return False

    def set_create(self, name, desc, data):
        try:
            self.conn.cursor().execute('CREATE %s %s %s' % (name, desc, data))
            return True
        except Exception as e:
            if self.log:
                write_log('create %s exception:%s' % (name, e))
            return False

    def set_drop(self, name, desc):
        try:
            self.conn.cursor().execute('DROP %s %s' % (name, desc))
            return True
        except Exception as e:
            if self.log:
                write_log('drop %s:%s exception:%s' % (name, desc, e))
            return False

    def set_insert(self, table, desc, data):
        try:
            self.conn.cursor().execute('insert into %s(%s) values(%s)' % (table, desc, data))
            return True
        except Exception as e:
            if self.log:
                write_log('insert exception:%s' % e)
            return False

    def set_update(self, table, desc, data, condition=''):
        try:
            if condition == '':
                self.conn.cursor().execute('UPDATE %s set (%s) = (%s)' % (table, desc, data))
            else:
                self.conn.cursor().execute('UPDATE %s set (%s) = (%s) where %s' % (table, desc, data, condition))
            return True
        except Exception as e:
            if self.log:
                write_log('update exception:%s' % e)
                write_log('update exception:%s' % desc)
                write_log('update exception:%s' % data)
            return False

    def set_replace(self, table, desc, data):
        try:
            self.conn.cursor().execute('replace into %s(%s) values(%s)' % (table, desc, data))
            return True
        except Exception as e:
            if self.log:
                write_log('replace exception:%s' % e)
            return False

    def set_delete(self, table, desc, data):
        try:
            self.conn.cursor().execute('delete from %s where %s=%s' % (table, desc, data))
            self.conn.commit()
            return True
        except Exception as e:
            if self.log:
                write_log('delete exception:%s' % e)
            return False

    def get_select(self, table, desc, condition=''):
        try:
            if condition == '':
                data = self.conn.cursor().execute('select %s from %s' % (desc, table)).fetchall()
            else:
                data = self.conn.cursor().execute('select %s from %s WHERE %s' % (desc, table, condition)).fetchall()
            return data
        except Exception as e:
            if self.log:
                write_log('select exception:%s' % e)
            return False

    def get_condition(self, desc):
        try:
            data = self.conn.cursor().execute(desc).fetchall()
            return data
        except Exception as e:
            if self.log:
                write_log('condition exception:%s' % e)
            return False

    def set_commit(self):
        try:
            self.conn.commit()
            return True
        except Exception as e:
            if self.log:
                write_log('commit exception:%s' % e)
            return False


class MyExcel(object):
    def __init__(self, log=True):
        self.log = log

    def write(self, file, head, data):
        try:
            wb = xlwt.Workbook()
            _row = 0
            _data_row = 0
            ws = wb.add_sheet('Sheet1')
            for i, _col in enumerate(head.split(',')):
                ws.write(_row, i, _col)
            for dat in data:
                if (_data_row % 50000) == 0 and _data_row > 0:
                    _row = 0
                    ws = wb.add_sheet('Sheet%d' % (int(_data_row / 50000)+1))
                    for i, _col in enumerate(head.split(',')):
                        ws.write(_row, i, _col)
                _row += 1
                _data_row += 1
                for i, _col in enumerate(dat):
                    ws.write(_row, i, _col)
            wb.save(file)
        except Exception as e:
            if self.log:
                write_log('Excel write exception: %s' % e)
            return False
        return True

    def read(self, file):
        _list = []
        try:
            wb = xlrd.open_workbook(file)
            ws = wb.sheet_by_index(0)
            for i in range(ws.nrows):
                _list.append(ws.row_values(i))
        except Exception as e:
            if self.log:
                write_log('Excel read exception: %s' % e)
            return False
        if not len(_list) > 0:
            return False
        return _list


class MyOs(object):
    def __init__(self, log=True):
        self.log = log

    def get_current_path(self):
        _path = os.getcwd()
        if self.log:
            write_log('Current path:%s' % _path)
        return _path


class MySocket(object):
    def __init__(self, log=True):
        self.log = log
        self.local_ip = self.get_ip()
        self.local_port = 0
        self.local_addr = None
        self.remote_ip = self.local_ip
        self.remote_port = 0
        self.remote_addr = None
        self.sock_udp = None
        self.sock_tcp = None
        self.sock_client = None

        self.receive = ''
        self.buffer = ''
        self.timeout = 50
        self.rx_qq = queue.Queue()

    def set_timeout(self, ts):
        self.timeout = ts
        
    def cls_rx(self):
        self.rx_qq.queue.clear()

    def get_ip(self):
        myaddrs = socket.getaddrinfo(socket.gethostname(), None)
        for addr in myaddrs:
            if str(addr[0]) == 'AddressFamily.AF_INET':
                ip = str(addr[4][0])
                ip = [int(x) for x in ip.split('.')]
                if 1 < ip[3] < 255:
                    return '{}.{}.{}.{}'.format(ip[0], ip[1], ip[2], ip[3])
        if self.log:
            write_log('get_ip except: can not found ip addr')
        return '127.0.0.1'

    def udp_new_server(self, local, remote=8888):
        self.remote_addr = ('<broadcast>', remote)
        try:
            self.sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock_udp.bind((self.local_ip, local))
            self.sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.sock_udp.settimeout(self.timeout/1000)
            return True
        except Exception as e:
            if self.log:
                write_log('create_udp_server except: {}'.format(e))
        return False

    def udp_recv_data(self):
        try:
            assert isinstance(self.sock_udp, socket.socket)
            data, addr = self.sock_udp.recvfrom(2000)
            if addr:
                self.remote_addr = addr
            if data:
                data = data.decode('utf-8', 'ignore')
            return data
        except Exception as e:
            if str(e) == 'timed out':
                pass
            elif self.log:
                write_log('udp_recv_data except: {}'.format(e))
        return None

    def udp_send_data(self, data):
        try:
            assert isinstance(self.sock_udp, socket.socket)
            data = data.encode('utf-8', 'ignore')
            self.sock_udp.sendto(data, self.remote_addr)
            return True
        except Exception as e:
            if self.log:
                write_log('udp_send_data except: {}'.format(e))
        return False

    def udp_sendby(self, tx, rx, wait=True):
        self.buffer = ''
        self.receive = ''

        if not self.udp_send_data(tx):
            return False
        if not wait:
            return True

        _start = int(round(time() * 1000))
        _now = int(round(time() * 1000))
        while _now - _start < self.timeout:
            line = self.udp_recv_data()
            if line:
                self.buffer += line
                _start = int(round(time() * 1000))
                if rx in self.buffer:
                    break
            _now = int(round(time() * 1000))
            sleep(0.01)
        if self.buffer:
            if self.log:
                write_log('udp_sendby rx:{}'.format(self.buffer))
            for d in self.buffer.split('\n'):
                self.rx_qq.put(d)
        if self.buffer and rx in self.buffer:
            self.receive = self.buffer[self.buffer.rfind(rx):]
            return True
        else:
            self.receive = self.buffer
        return False

    def tcp_new_server(self, port, num=1):
        try:
            self.local_addr = (self.local_ip, int(port))
            self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock_tcp.bind(self.local_addr)
            self.sock_tcp.listen(int(num))
            self.sock_tcp.settimeout(self.timeout/1000)
            return True
        except Exception as e:
            if self.log:
                write_log('tcp_new_server except: {}'.format(e))
        return False

    def tcp_new_client(self, ip, port):
        try:
            self.remote_addr = (str(ip), int(port))
            self.sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock_client.connect(self.remote_addr)
            self.sock_client.settimeout(self.timeout/1000)
            return True
        except Exception as e:
            if self.log:
                write_log('tcp_new_client except: {}'.format(e))
        return False

    def tcp_recv_accept(self):
        try:
            assert isinstance(self.sock_tcp, socket.socket)
            client, addr = self.sock_tcp.accept()
            if addr:
                self.remote_addr = addr
            if client:
                self.sock_client = client
            return True
        except Exception as e:
            if str(e) == 'timed out':
                pass
            elif self.log:
                write_log('tcp_get_accept except: {}'.format(e))
        return False

    def tcp_recv_data(self):
        try:
            assert isinstance(self.sock_client, socket.socket)
            data = self.sock_client.recv(2000)
            if data:
                data = data.decode('utf-8', 'ignore')
                return data
        except Exception as e:
            if str(e) == 'timed out':
                pass
            elif self.log:
                write_log('tcp_recv_data except: {}'.format(e))
        return None

    def tcp_send_data(self, data):
        try:
            assert isinstance(self.sock_client, socket.socket)
            data = data.encode('utf-8', 'ignore')
            self.sock_client.send(data)
            return True
        except Exception as e:
            if self.log:
                write_log('tcp_send_data except: {}'.format(e))
        return False


class MyQt5(object):
    def __init__(self, log=True):
        self.log = log
        self.color_white = 'color: rgb(255, 255, 255);'
        self.color_black = 'color: rgb(0, 0, 0);'
        self.color_red = 'color: rgb(170, 0, 0);'
        self.color_green = 'color: rgb(0, 170, 0);'
        self.color_blue = 'color: rgb(85, 0, 255);'
