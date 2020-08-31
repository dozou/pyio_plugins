# -*- coding: utf-8 -*-
from ctypes import *
import sys
from analogdiscovery2.Core import CoreDriver, dwf, get_connection_devices
import analogdiscovery2.dwfconstants as dwfc
from pyio.Devices.IODevice import IODevice
import time


class AnalogOut(IODevice):
    def __init__(self, core: CoreDriver=CoreDriver(),ch:int=0):
        super(AnalogOut, self).__init__()
        self.core = core
        self.info["name"] = "AnalogDiscovery"
        self.info["type"] = "ao"
        self.info["ch"] = ch

    def is_open(self):
        return self.core.is_open()

    def open_device(self, index):
        return self.core.open_device(device_index=index)

    def close_device(self):
        self.core.close_device()

    def create_sweep(self, startHz, stopHz, sweepSec, outVoltage=1.0):
        channel = c_int(self.info["ch"] % 2)
        startHz = float(startHz)
        stopHz = float(stopHz)
        sweepSec = float(sweepSec)
        dwf.FDwfAnalogOutNodeEnableSet(self.core.hdwf, channel, dwfc.AnalogOutNodeCarrier, c_bool(True))
        dwf.FDwfAnalogOutNodeFunctionSet(self.core.hdwf, channel, dwfc.AnalogOutNodeCarrier, dwfc.funcSine)
        dwf.FDwfAnalogOutNodeSymmetrySet(self.core.hdwf, channel, dwfc.AnalogOutNodeCarrier, c_double(50))
        dwf.FDwfAnalogOutNodeFrequencySet(self.core.hdwf, channel, dwfc.AnalogOutNodeCarrier, c_double((stopHz+startHz)/2))
        dwf.FDwfAnalogOutNodeAmplitudeSet(self.core.hdwf, channel, dwfc.AnalogOutNodeCarrier, c_double(outVoltage))
        dwf.FDwfAnalogOutNodeOffsetSet(self.core.hdwf, channel, dwfc.AnalogOutNodeCarrier, c_double(0))
        dwf.FDwfAnalogOutNodeEnableSet(self.core.hdwf, channel, dwfc.AnalogOutNodeFM, c_bool(True))
        dwf.FDwfAnalogOutNodeFunctionSet(self.core.hdwf, channel, dwfc.AnalogOutNodeFM, dwfc.funcRampUp)
        dwf.FDwfAnalogOutNodeFrequencySet(self.core.hdwf, channel, dwfc.AnalogOutNodeFM, c_double(1.0/sweepSec))
        dwf.FDwfAnalogOutNodeAmplitudeSet(self.core.hdwf, channel, dwfc.AnalogOutNodeFM, c_double(100.0*(stopHz-startHz)/(startHz+stopHz)))
        dwf.FDwfAnalogOutNodeSymmetrySet(self.core.hdwf, channel, dwfc.AnalogOutNodeFM, c_double(100))
        dwf.FDwfAnalogOutNodeOffsetSet(self.core.hdwf, channel, dwfc.AnalogOutNodeFM, c_double(0))
        self.__start()

    def create_custom_wave(self, customWave, period, outVoltage=1.0):
        self.__reset()
        channel = c_int(self.info["ch"] % 2)
        samples = (c_double*len(customWave))()
        for i,data in enumerate(customWave):
            samples[i] = c_double(data)
        dwf.FDwfAnalogOutNodeEnableSet(self.core.hdwf, channel, dwfc.AnalogOutNodeCarrier, c_bool(True))
        dwf.FDwfAnalogOutNodeFunctionSet(self.core.hdwf, channel, dwfc.AnalogOutNodeCarrier, dwfc.funcCustom)
        dwf.FDwfAnalogOutNodeDataSet(self.core.hdwf, channel, dwfc.AnalogOutNodeCarrier, samples, c_int(len(customWave)))
        dwf.FDwfAnalogOutNodeFrequencySet(self.core.hdwf, channel, dwfc.AnalogOutNodeCarrier, c_double(1.0/period))
        dwf.FDwfAnalogOutNodeAmplitudeSet(self.core.hdwf, channel, dwfc.AnalogOutNodeCarrier, c_double(outVoltage))
        dwf.FDwfAnalogOutNodeOffsetSet(self.core.hdwf, channel, dwfc.AnalogOutNodeCarrier, c_double(0))
        self.__start()

    def __reset(self):
        dwf.FDwfAnalogOutReset(self.core.hdwf, c_int(self.info["ch"] % 2))

    def __start(self):
        dwf.FDwfAnalogOutConfigure(self.core.hdwf, c_int(self.info["ch"] % 2), c_int(1))


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    print(get_connection_devices())
    ao_dev = AnalogOut()
    ao_dev.open_device(0)

    ao_dev.create_sweep(1000, 3500, 0.05, 2.5)
    time.sleep(5)
    ao_dev.close_device()
