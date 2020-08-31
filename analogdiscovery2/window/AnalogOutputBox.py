# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPushButton
from pyio.Window.LineEdit import LabelOnSpinBox
from analogdiscovery2.AnalogOut import AnalogOut


class AnalogOutputBox(QGroupBox):
    def __init__(self, devices: list):
        super(AnalogOutputBox, self).__init__()
        self.setTitle("AnalogOut")
        self.devices = devices

        self.start_hz = LabelOnSpinBox("Start [Hz]",
                                       maximum=500000,
                                       val=1000)

        self.stop_hz = LabelOnSpinBox("Stop [Hz]",
                                      maximum=500000,
                                      val=3500)
        self.period = LabelOnSpinBox("Period [ms]",
                                     maximum=10000.00,
                                     val=50.0)
        self.voltage = LabelOnSpinBox("Voltage [V]",
                                      maximum=5.0,
                                      val=2.5)

        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.clicked_update)
        layout = QVBoxLayout()
        layout.addWidget(self.start_hz)
        layout.addWidget(self.stop_hz)
        layout.addWidget(self.period)
        layout.addWidget(self.voltage)
        layout.addWidget(self.update_button)
        layout.addStretch()
        self.setLayout(layout)

    def clicked_update(self):
        for i in self.devices:  # type: AnalogOut
            if i.info["name"] == "AnalogDiscovery" and i.info["type"] == "ao":
                i.create_sweep(
                    startHz=self.start_hz.get_value(),
                    stopHz=self.stop_hz.get_value(),
                    sweepSec=self.period.get_value()/1000.0,
                    outVoltage=self.voltage.get_value()
                )
