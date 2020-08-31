# -*- coding: utf-8 -*-
from ctypes import *
import sys
from analogdiscovery2.Core import CoreDriver, dwf, get_connection_devices
import analogdiscovery2.dwfconstants as dwfc
from pyio.Devices.IODevice import IODevice
import time


class AnalogIn(IODevice):
    def __init__(self, core: CoreDriver=CoreDriver(),ch:int=0):
        super(AnalogIn, self).__init__()
        self.core = core
        self.samples = 0
        self.sample_rate = 0
        self.info["name"] = "AnalogDiscovery"
        self.info["type"] = "ai"
        self.info["ch"] = ch
        self.info["samples"] = self.samples
        self.info["sample_rate"] = self.sample_rate

    def is_open(self):
        return self.core.is_open()

    def open_device(self, index):
        return self.core.open_device(device_index=index)

    def close_device(self):
        self.core.close_device()

    def set_property(self, sample_rate, samples, mode=dwfc.acqmodeScanShift):
        # print(self.core.hdwf)
        self.samples = samples
        self.sample_rate = sample_rate
        dwf.FDwfAnalogInChannelEnableSet(self.core.hdwf, c_int(0), c_bool(True))
        dwf.FDwfAnalogInChannelRangeSet(self.core.hdwf, c_int(0), c_double(10))
        dwf.FDwfAnalogInAcquisitionModeSet(self.core.hdwf, mode)  # (1)acqmodeScanShift (2)ScanScreen (3)Record
        dwf.FDwfAnalogInFrequencySet(self.core.hdwf, c_double(sample_rate))
        dwf.FDwfAnalogInBufferSizeSet(self.core.hdwf, c_int(samples))
        time.sleep(2)
        dwf.FDwfAnalogInConfigure(self.core.hdwf, c_int(2), c_int(1))
        pass

    def get_1d_array(self):
        return self.get_2d_array()[self.info['ch'] % 2]

    def get_2d_array(self):
        sts = c_byte()
        cValid = c_int(0)
        index = c_int(0)
        rgdSamples = (c_double * self.samples)()
        rgdSamples2 = (c_double * self.samples)()

        rgpy = [0.0] * len(rgdSamples)
        rgpy2 = [0.0] * len(rgdSamples)
        error_cnt = 0
        if not self.is_open():
            return rgpy, rgpy2

        while True:
            dwf.FDwfAnalogInStatus(self.core.hdwf, c_int(1), byref(sts))
            dwf.FDwfAnalogInStatusSamplesValid(self.core.hdwf, byref(cValid))
            # get samples
            dwf.FDwfAnalogInStatusData(self.core.hdwf, c_int(0), byref(rgdSamples), cValid)
            dwf.FDwfAnalogInStatusIndexWrite(self.core.hdwf, byref(index))
            dwf.FDwfAnalogInStatusData(self.core.hdwf, c_int(1), byref(rgdSamples2), cValid)
            dwf.FDwfAnalogInStatusIndexWrite(self.core.hdwf, byref(index))
            for i in range(0, cValid.value):
                rgpy[i] = rgdSamples[i]
                rgpy2[i] = rgdSamples2[i]
            if cValid.value > 0:
                return rgpy, rgpy2
            if error_cnt > 100:
                raise IOError("Not device communication.")
            error_cnt += 1

    def get_serial(self):
        return self.core.get_serial()


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    """
    接続されたデバイス全てのAnalogInputデータを表示するサンプル
    """

    """複数接続を行うためデバイスオープンを実施（単体で使用する場合AnalogInputのみ）"""
    core_device = []
    for i in get_connection_devices():
        c = CoreDriver()
        c.open_device(i[0])
        core_device.append(c)

    """接続されたデバイスにチャンネルを設定：AnalogInputのインスタンス生成"""
    ch = 0
    analog_input_device = []
    for i in core_device:
        ai = AnalogIn(i, ch)
        analog_input_device.append(ai)
        ch += 1
        ai = AnalogIn(i, ch)
        analog_input_device.append(ai)
        ch += 1

    """格納されているデバイスリストから設定を更新"""
    for i in analog_input_device:
        i.set_property(sample_rate=163840, samples=4096)

    """表示系を整える"""
    plt.axis([0, analog_input_device[0].samples, -2, 2])
    plt.ion()
    hl = []
    for i in analog_input_device:
        l, = plt.plot([], [])
        l.set_xdata(list(range(0, i.samples)))
        hl.append(l)

    i = int(0)
    while True:
        i += 1
        if i == 300:
            break
        for dev, l in zip(analog_input_device, hl):
            print(dev.info['ch'])
            l.set_ydata(dev.get_1d_array())

        plt.draw()
        plt.pause(0.03)

    for i in core_device:
        i.close_device()
