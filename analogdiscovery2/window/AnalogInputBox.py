# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPushButton
from pyio.Window.LineEdit import LabelOnSpinBox
from analogdiscovery2.AnalogIn import AnalogIn


class AnalogInputBox(QGroupBox):
    def __init__(self, devices:list):
        super(AnalogInputBox, self).__init__()
        self.setTitle("AnalogInput")
        self.devices = devices
        self.sample_rate = LabelOnSpinBox("Sample rate",
                                          maximum=163840*10,
                                          val=163840)
        self.samples = LabelOnSpinBox("Samples",
                                      maximum=8192,
                                      val=8192)
        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.clicked_update)
        layout = QVBoxLayout()
        layout.addWidget(self.sample_rate)
        layout.addWidget(self.samples)
        layout.addWidget(self.update_button)
        layout.addStretch()
        self.setLayout(layout)

    def clicked_update(self):
        for i in self.devices:  # type: AnalogIn
            if i.info["name"] == "AnalogDiscovery" and i.info["type"] == "ai":
                i.info["samples"] = self.samples.get_value()
                i.info["sample_rate"] = self.sample_rate.get_value()
                i.set_property(
                    sample_rate=self.sample_rate.get_value(),
                    samples=self.samples.get_value()
                )
