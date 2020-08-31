from pybration.Main import main
from pybration.DataSturucture import Plugin, DataContainer
from yapsy.IPlugin import IPlugin
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QTimer
import TweModule.TweLiteBasic as TweModule


class GripSensor(TweModule.TweLiteBasic):
    def __init__(self, record_device=None):
        super().__init__("/dev/tty.usbserial-MWHCYFV")
        self.info['name'] = "GripSensor"

    def get_value(self)->float:
        volt = self.device_io.vin / 1000.0
        vout = self.device_io.ai[0] / 1000.0
        if volt - vout == 0:
            return 0
        r2 = (2960 * vout) / (volt - vout)
        grip_force = (r2 - 196) / 163.8
        return grip_force


class GripForceSensor(QWidget, DataContainer):
    def __init__(self, data: DataContainer):
        super().__init__()
        self.setWindowTitle("GripForceSensor")

        self.connect_button = QPushButton("Start")
        self.connect_button.clicked.connect(self.connect_sensor)
        self.value = QLabel()

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update)
        self.timer.start()

        self.device = GripSensor()
        data.device.append(self.device)

        layout = QVBoxLayout()
        layout.addWidget(self.connect_button)
        layout.addWidget(self.value)
        self.setLayout(layout)

    def update(self):
        self.value.setText(('%03.3f' % self.device.get_value())+" [N]")
        pass

    def connect_sensor(self):
        self.connect_button.disconnect()
        self.connect_button.clicked.connect(self.disconnect_sensor)
        self.connect_button.setText("Stop")
        self.device.start()
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update)
        self.timer.start()
        pass

    def disconnect_sensor(self):
        self.connect_button.disconnect()
        self.connect_button.clicked.connect(self.connect_sensor)
        self.connect_button.setText("Start")
        self.device.stop()
        self.timer = None
        pass


class Viewer(Plugin):
    def __init__(self):
        super().__init__()
        self.window = None  # type:GripForceSensor

    def init(self, data):
        self.data = data

    def clicked(self):
        self.window = GripForceSensor(self.data)
        self.window.show()
        self.data.parameter['Plugins']['握力計測デバイス']["Test"] = "test"

    def enable_button(self):
        return True


if "__main__" == __name__:
    main()
