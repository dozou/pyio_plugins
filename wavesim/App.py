# -*- coding: utf-8 -*-
from pyio.DataSturucture import Plugin
from pyio.Main import main
from wavesim.Window import Window


class App(Plugin):
    def __init__(self):
        super().__init__()
        self.window = None

    def init(self, data):
        self.data = data
        self.window = Window(data=data)

    def enable_button(self):
        return True

    def clicked(self):
        self.window.show()



if __name__ == '__main__':
    main()