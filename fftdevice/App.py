# -*- coding: utf-8 -*-
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
from pyio.DataSturucture import Plugin, DataContainer
from pyio.Devices.IODevice import IODevice
from pyio.Util import System
from pyio.Main import main
import scipy.fftpack as fftpack
import numpy as np
import pickle
import pandas as pd


class FFTDevice(IODevice):

    def __init__(self, device: IODevice):
        super(FFTDevice, self).__init__()
        self.info['name'] = "FFTDevice"
        self.info['type'] = "ai"
        self.info['ch'] = device.info["ch"]
        self.device = device
        self.xscale = fftpack.fftfreq(n=int(device.info['samples']), d=1/device.info['sample_rate'])

    def open_device(self):
        pass

    def is_open(self):
        return True

    def close_device(self):
        pass

    def get_1d_array(self):
        data = self.device.get_1d_array()
        fft_data = fftpack.fft(x=data, n=8192)
        a = np.array([i.real**2 + i.imag**2 for i in fft_data])
        # a = 20 * np.log10(a)
        a = np.sqrt(a)
        return a

    def get_x_scale(self):
        return self.xscale


class Window(QWidget):
    def __init__(self, data:DataContainer):
        super(Window, self).__init__()
        self.device = data.device
        self.sys = System()
        button = QPushButton("追加")
        button.clicked.connect(self.add_device)
        data_button = QPushButton("保存")
        data_button.clicked.connect(self.save_data)
        layout = QVBoxLayout()
        layout.addWidget(button)
        layout.addWidget(data_button)
        layout.addStretch()
        self.setLayout(layout)

    def add_device(self):
        ai_device = []
        for dev in self.device:
            if dev.info["name"] == "AnalogDiscovery" and dev.info["type"] == 'ai':
                ai_device.append(dev)

        for dev in ai_device:
            self.device.append(FFTDevice(dev))
        self.device.print()

    def save_data(self):
        for dev in self.device:
            if dev.info["name"] == "FFTDevice":
                a = dev.get_1d_array()
                # print(a)
                print(a.shape)
                with open(self.sys.get_work_dir()+"FFTDevice.pkl", "bw") as fp:
                    pickle.dump(a, fp)
                    print("書き出し完了")


class App(Plugin):
    def __init__(self):
        super().__init__()
        # self.setWindowFlags(Qt.Dialog)
        self.window = None

    def init(self, data):
        self.data = data
        self.window = Window(self.data)

    def enable_button(self):
        return True

    def clicked(self):
        self.window.show()


if "__main__" == __name__:
    main()
