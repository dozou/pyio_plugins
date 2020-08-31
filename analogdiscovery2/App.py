# -*- coding: utf-8 -*-
from pyio.DataSturucture import Plugin
from pyio.Main import main
from analogdiscovery2.window.SettingWindow import SettingWindow


class App(Plugin):
    def __init__(self):
        super().__init__()
        self.window = None

    def init(self, data):
        self.window = SettingWindow(data)
        self.window.setWindowTitle("WaveForms")

    def enable_setting_window(self):
        return True

    def get_setting_window(self):
        return self.window


if "__main__" == __name__:
    main()
