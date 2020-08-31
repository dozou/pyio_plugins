# -*- coding: utf-8 -*-
from ctypes import *
import time
import sys
import threading as th
from pyio.Devices.IODevice import IODevice

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")


def get_connection_count():
    """
    test
    @return: 現在，接続されているAD2の数を整数値で返す
    """
    devices = c_int()
    dwf.FDwfEnum(c_int(0), byref(devices))
    return devices.value


def get_serial(device_index: int):
    """

    @param device_index: 接続されているAD2のデバイス接続ID
    @return: 渡されたデバイスIDに対応するシリアルナンバーを返す
    """
    device_index = c_int(device_index)
    serial_num = create_string_buffer(16)
    dwf.FDwfEnumSN(device_index, serial_num)
    serial_num = str(serial_num.value)
    serial_num = serial_num.replace("b'", "")
    serial_num = serial_num.replace("'", "")
    return serial_num


def get_index(serial_num: str):
    """

    @param serial_num: 任意のAD2のシリアルナンバー
    @return: シリアルナンバーに対応した接続IDを整数値で返却
    """
    for i in range(get_connection_count()):
        if get_serial(i) == serial_num:
            return i


def get_connection_devices():
    """
    :return: [(index, serial), ...]
    """
    return [(i, get_serial(i)) for i in range(get_connection_count())]


class CoreDriver(IODevice):

    def __init__(self):
        super(CoreDriver, self).__init__()
        self.hdwf = c_int()
        self.is_open_device = c_bool()
        self.device_index = c_int(0)
        self.info['name'] = 'AnalogDiscoveryCore'
        self.info['type'] = 'core_device'
        get_connection_devices()

    def __del__(self):
        self.close_device()

    def is_open(self):
        # dwf.FDwfEnumDeviceIsOpened(self.device_index, byref(self.is_open_device))
        return self.is_open_device

    def open_device(self, device_index: int):
        self.device_index = c_int(device_index)
        dwf.FDwfEnumDeviceIsOpened(self.device_index, byref(self.is_open_device))
        if not self.is_open_device:
            dwf.FDwfDeviceOpen(self.device_index, byref(self.hdwf))
            self.is_open_device = c_bool(True)
            return True
        return False

    def close_device(self):
        if self.is_open_device:
            # print(self.hdwf)
            dwf.FDwfDeviceClose(self.hdwf)
            self.is_open_device = c_bool(False)

    def get_serial(self):
        serial_num = create_string_buffer(16)
        dwf.FDwfEnumSN(self.device_index, serial_num)
        serial_num = str(serial_num.value)
        serial_num = serial_num.replace("b'", "")
        serial_num = serial_num.replace("'", "")
        return serial_num


if __name__ == '__main__':
    print(get_connection_count())
    print(get_connection_devices())

    connected_device_list = get_connection_devices()

    device = []
    for i in get_connection_devices():
        t = CoreDriver()
        t.open_device(i[0])
        print(t.hdwf)
        device.append(t)

    print(device)
    dwf.FDwfDeviceCloseAll()




