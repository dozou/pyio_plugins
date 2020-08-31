# -*- coding: utf-8 -*-
from pyio.DataSturucture import Plugin, DataContainer
from pyio.Main import main
from signal_viewer.Window import Viewer


class App(Plugin):
    def __init__(self):
        super(App, self).__init__()
        self.window = None  # type:Viewer
        self.data = None

    def init(self, parent_data: DataContainer):
        self.data = parent_data

    def enable_button(self):
        return True

    def clicked(self):
        self.window = Viewer(data=self.data)
        self.window.show()


if __name__ == '__main__':
    main()
