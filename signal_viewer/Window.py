# -*- coding: utf-8 -*-
from pyio.DataSturucture import DataContainer
from pyio.Window.LineEdit import LabelOnSpinBox, RangeView
from signal_viewer.Charts import ChartObject
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QChartView
from PyQt5.Qt import Qt
import numpy as np

class ChartWidget(QWidget):
    def __init__(self, device, parent=None):
        super().__init__(parent)
        self.ch = ChartObject(devices=device)
        self.view = QChartView(self.ch.chart)
        self.view.setRenderHint(QPainter.Antialiasing)
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.resize(500, 800)

        self.color = Qt.black

    def set_title(self, title):
        self.ch.chart.setTitle(title)

    # def set_data(self, device, color):
    #     self.color = color
    #     self.device = device


class ControlPanel(QGroupBox):
    def __init__(self, chart:ChartWidget):
        super(ControlPanel, self).__init__()
        self.ch = chart
        self.setTitle("操作")
        self.y_range = RangeView(-5, 5)
        self.y_range.changed_value(self.update_y_range)
        self.auto_detect_button = QPushButton("Auto")
        self.auto_detect_button.clicked.connect(self.__auto_y_range)
        self.x_range = RangeView()
        self.x_range.changed_value(self.update_x_range)
        # self.y_plus_range = LabelOnSpinBox("+Y",1000, 5)
        # self.y_minus_range = LabelOnSpinBox("-Y", 1000, -5)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Y-Range"))
        layout.addWidget(self.y_range)
        layout.addWidget(self.auto_detect_button)
        layout.addWidget(QLabel("X-Range"))
        layout.addWidget(self.x_range)
        # layout.addWidget(self.y_plus_range)
        # layout.addWidget(self.y_minus_range)
        layout.addStretch()
        self.setLayout(layout)
        self.__auto_y_range()

    def update_y_range(self):
        self.ch.ch.set_y_range(self.y_range.get_value()[0], self.y_range.get_value()[1])

    def update_x_range(self):
        self.ch.ch.set_x_range(self.x_range.get_value()[0], self.x_range.get_value()[1])

    def __auto_y_range(self):
        max = 0
        min = 0
        for dev in self.ch.ch.device:
            d = dev.get_1d_array()
            max_temp = np.max(d)
            min_temp = np.min(d)
            if max_temp > max:
                max = max_temp
            if min_temp < min:
                min = min_temp
        self.ch.ch.set_y_range(min, max)
        self.y_range.start.setValue(min)
        self.y_range.stop.setValue(max)


class Viewer(QWidget):
    def __init__(self,parent=None, data: DataContainer=None):
        super().__init__(parent)
        device = data.device
        self.setWindowTitle("RawSignalViewer")
        self.chart_widgets = []

        self.ai_device_name = set()
        for i in device:
            if i.info["type"] == "ai":
                self.ai_device_name.add(i.info['name'])

        sorted(self.ai_device_name)
        for name in self.ai_device_name:
            l = []
            for i in device:
                if name == i.info['name'] and "ai" == i.info['type']:
                    l.append(i)
            ch = ChartWidget(device=l)
            ch.set_title(name)
            self.chart_widgets.append(ch)
        #
        main_layout = QVBoxLayout()
        # main_layout.addWidget(self.ctrl_panel)

        for i, obj in enumerate(self.chart_widgets):
            layout = QHBoxLayout()
            layout.addWidget(obj)
            layout.addWidget(ControlPanel(obj))
            main_layout.addLayout(layout)

        self.setLayout(main_layout)
        self.resize(1000, 500)

    def hideEvent(self, e):
        for i in self.chart_widgets:
            i.ch.timer.stop()
