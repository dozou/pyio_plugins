# -*- coding: utf-8 -*-
from PyQt5.Qt import Qt
from pyio.DataSturucture import Plugin, DataContainer
from pyio.Main import main
import sys
import recoder_v1.Window as Recoder_v1

class App(Plugin):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.opend_window = False
        self.view = None

    def init(self, parent_data: DataContainer):
        # print(sys.path)
        # pass
        self.view = Recoder_v1.Viewer(data_container=parent_data)

    def enable_button(self):
        return True

    def clicked(self):
        # self.view.show()

        if not self.opend_window:
            self.opend_window = True
            self.view.window_create()

        self.view.window_init()
        self.view.show()


if "__main__" == __name__:
    main()
