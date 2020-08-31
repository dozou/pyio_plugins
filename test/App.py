# -*- coding: utf-8 -*-
from PyQt5.Qt import Qt
from pyio.DataSturucture import Plugin
from pyio.Main import main


class App(Plugin):
    def __init__(self):
        super().__init__()
        # self.setWindowFlags(Qt.Dialog)
        self.window = None

    def init(self, data):
        self.data = data

    def enable_button(self):
        return True

    def clicked(self):
        print("click!!")


if "__main__" == __name__:
    main()
