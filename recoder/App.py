# -*- coding: utf-8 -*-
from pyio.Main import main
from pyio.DataSturucture import Plugin, DataContainer
from recoder.Recorder import Viewer


class App(Plugin):

    def __init__(self):
        super(App, self).__init__()
        self.view = None  # type: Viewer

    def init(self, parent_data: DataContainer):
        self.view = Viewer(data_container=parent_data)

    def enable_button(self):
        return True

    def clicked(self):
        self.view.show()


if __name__ == '__main__':
    main()
