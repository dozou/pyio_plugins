# -*- coding: utf-8 -*-
import numpy as np
import pickle
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSlider
from PyQt5.QtWidgets import QLabel
from PyQt5.Qt import Qt
from pyio.DataSturucture import DataContainer
from pyio.Devices.IODevice import IODevice
from pyio.Util import System


class WaveEmulateDevice(IODevice):

    def __init__(self):
        super(WaveEmulateDevice, self).__init__()
        self.info['name'] = 'AIEmulator'
        self.info['type'] = 'ai'
        self.info['ch'] = 0
        self.phase = 0
        self.freq = 1
        self.amp = 1.0

    def open_device(self):
        pass

    def close_device(self):
        pass

    def is_open(self):
        return True

    def set_value(self, freq, phase, amp):
        self.freq = freq
        self.phase = phase
        self.amp = amp

    def get_1d_array(self):
        N = 8192
        data = np.zeros((N,), dtype=np.float64)
        for i, d in enumerate(data):
            data[i] = i*self.freq*(np.pi*2/N)+(self.phase*(np.pi/180.0))
        # data = np.arange(self.phase*(np.pi/180.0), self.phase*(np.pi/180.0)+np.pi*2*self.freq, 0.01)
        data = self.amp*np.sin(data)
        return data

    def get_serial(self):
        return 'EmulatorDevice'


class Window(QWidget):
    def __init__(self, data: DataContainer):
        super(Window, self).__init__()
        self.setWindowFlags(Qt.Dialog)
        self.data = data
        self.button = QPushButton("デバイス確認")
        self.button.clicked.connect(self.data.device.print)
        self.add_device_button = QPushButton("デバイス追加")
        self.add_device_button.clicked.connect(self.__add_device)
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.__save_wave)

        self.phase_slide_label = QLabel("位相")
        self.phase_slide = QSlider(Qt.Horizontal)
        self.phase_slide.setRange(0, 180)
        self.phase_slide.valueChanged.connect(self.__changed_slide)

        self.freq_slide_label = QLabel("周波数")
        self.freq_slide = QSlider(Qt.Horizontal)
        self.freq_slide.setRange(1.0, 50.0)
        self.freq_slide.valueChanged.connect(self.__changed_slide)

        self.amp_slide_label = QLabel("振幅")
        self.amp_slide = QSlider(Qt.Horizontal)
        self.amp_slide.setRange(1.0, 5.0)
        self.amp_slide.valueChanged.connect(self.__changed_slide)

        self.device = WaveEmulateDevice()
        self.update_layout()

    def __add_device(self):
        self.data.device.append(self.device)

    def __changed_slide(self):
        self.device.set_value(self.freq_slide.value(),
                              self.phase_slide.value(),
                              self.amp_slide.value())

    def __save_wave(self):
        sys = System()
        file_name = sys.get_work_dir()+"EmuWave.pkl"
        with open(file_name, "wb") as fp:
            pickle.dump(self.device.get_1d_array(), fp)
            print(file_name+":書き出し完了")
        # with open(sys.get_work_dir())

    def update_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.add_device_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.phase_slide_label)
        layout.addWidget(self.phase_slide)
        layout.addWidget(self.freq_slide_label)
        layout.addWidget(self.freq_slide)
        layout.addWidget(self.amp_slide_label)
        layout.addWidget(self.amp_slide)
        layout.addStretch()
        self.setLayout(layout)

