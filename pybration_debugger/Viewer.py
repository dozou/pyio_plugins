from pyio.Main import main
from pyio.DataSturucture import Plugin
from pyio.DataSturucture import DataContainer
from yapsy.IPlugin import IPlugin
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtGui import QHideEvent
from PyQt5.QtCore import QTimer, pyqtSignal
import time
import sys


class Window(QWidget):
    hide_signal = pyqtSignal()

    def __init__(self, data: DataContainer, parent=None):
        super().__init__(parent=parent)
        self.data = data
        system_label = QLabel(str(sys.version))
        button_1 = QPushButton("device")
        button_1.clicked.connect(self.button_1)
        button_2 = QPushButton("enviroment_variable")
        button_2.clicked.connect(self.button_2)
        self.button_3 = QPushButton()
        self.button_3.setText("aaa")
        self.button_3.clicked.connect(self.button_3_func)

        layout = QVBoxLayout()
        layout.addWidget(system_label)
        layout.addWidget(button_1)
        layout.addWidget(button_2)
        layout.addWidget(self.button_3)
        self.setLayout(layout)

    def button_1(self):
        print(self.data.device)
        for dev in self.data.device:
            print(dev.info)
        pass

    def button_2(self):
        print(self.data.parameter)
        pass

    def button_3_func(self):
        self.data.device.print()
        # self.button_3.setDisabled(True)

    def hideEvent(self, a0: QHideEvent):
        self.hide_signal.emit()


class App(Plugin):
    def __init__(self):
        super().__init__()
        self.window = None

    def init(self, data):
        self.data = data

    def enable_button(self):
        return True

    def clicked(self):
        if self.window is None:
            self.window = Window(self.data)
        else:
            print("raihu")
        self.window.show()


if __name__ == "__main__":
    main()
    print("")
