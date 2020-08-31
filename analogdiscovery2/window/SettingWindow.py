# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.Qt import QFont
from pyio.DataSturucture import DataContainer, DeviceManager
from pyio.Devices.IODevice import IODevice
from analogdiscovery2.Core import CoreDriver, get_connection_devices
from analogdiscovery2.AnalogIn import AnalogIn
from analogdiscovery2.AnalogOut import AnalogOut
from analogdiscovery2.window.AnalogInputBox import AnalogInputBox
from analogdiscovery2.window.AnalogOutputBox import AnalogOutputBox


class SettingWindow(QWidget):
    def __init__(self, data: DataContainer):
        super(SettingWindow, self).__init__()
        """デバイス関連のインスタンス生成"""
        self.devices = data.device
        self.device_list = []
        self.device_core_list = DeviceManager()
        self.ai_device = []
        self.ao_device = []

        """UI関連のインスタンス生成"""
        self.connect_button = QPushButton("connect")
        self.disconnect_button = QPushButton("disconnect")
        self.disconnect_button.setEnabled(False)
        self.update_device_list()
        self.ai_panel = AnalogInputBox(self.devices)
        self.ai_panel.setEnabled(False)
        self.ao_panel = AnalogOutputBox(self.devices)
        self.ao_panel.setEnabled(False)

        """signal/slotの設定関数呼び出し"""
        self.connect_buttons()
        """UIレイアウトの更新"""
        self.update_layout()

    def connect_buttons(self):
        self.connect_button.clicked.connect(self.clicked_connect_button)
        self.disconnect_button.clicked.connect(self.clicked_disconnect_button)

    def update_layout(self):
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.connect_button)
        left_layout.addWidget(self.disconnect_button)

        for i in self.device_list:
            txt = QLabel("%d: %s" % (i[0], i[1]))
            txt.setFont(QFont("Regular-Mono", 10))
            left_layout.addWidget(txt)
        left_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.ai_panel)
        main_layout.addWidget(self.ao_panel)

        self.setLayout(main_layout)

    def __add_ai_device(self):
        self.ai_device = []
        ch = 0
        for i, d in enumerate(self.device_core_list):
            self.ai_device.append(AnalogIn(d, ch))
            ch += 1
            self.ai_device.append(AnalogIn(d, ch))
            ch += 1
        for i in self.ai_device:
            self.devices.append(i)

    def __add_ao_device(self):
        self.ao_device = []
        ch = 0
        for i, d in enumerate(self.device_core_list):
            self.ao_device.append(AnalogOut(d, ch))
            ch += 1
            self.ao_device.append(AnalogOut(d, ch))
            ch += 1
        for i in self.ao_device:
            self.devices.append(i)
        pass

    def clicked_connect_button(self):
        """CoreDriverの追加"""
        self.device_core_list = []
        if len(self.device_list) == 0:
            return
        for i in self.device_list:
            dev = CoreDriver()
            if not dev.open_device(i[0]):
                return
            self.device_core_list.append(dev)
        """AnalogInputの追加"""
        self.__add_ai_device()

        """AnalogOutの追加"""
        self.__add_ao_device()

        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)
        self.ai_panel.setEnabled(True)
        self.ao_panel.setEnabled(True)
        pass

    def clicked_disconnect_button(self):
        for i in self.device_core_list:  # type: IODevice
            i.close_device()

        for i in self.ai_device:
            self.devices.delete(i.info["id"])

        for i in self.ao_device:
            self.devices.delete(i.info["id"])

        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.ao_panel.setEnabled(False)
        self.ai_panel.setEnabled(False)
        pass

    def update_device_list(self):
        self.device_list = get_connection_devices()
        pass
