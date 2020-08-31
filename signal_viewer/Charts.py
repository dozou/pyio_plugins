# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import threading
import time
from PyQt5.QtWidgets import *
from PyQt5.QtChart import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pyio.DataSturucture import *


def series_to_polyline(xdata, ydata):
    size = len(xdata)
    polyline = QPolygonF(size)
    pointer = polyline.data()
    dtype, tinfo = np.float, np.finfo  # integers: = np.int, np.iinfo
    pointer.setsize(2*polyline.size()*tinfo(dtype).dtype.itemsize)
    memory = np.frombuffer(pointer, dtype)
    memory[:(size-1)*2+1:2] = xdata
    memory[1:(size-1)*2+2:2] = ydata
    return polyline


class ChartObject:
    def __init__(self, devices: list):
        super().__init__()
        self.chart = QChart()
        # self.chart.legend().hide()
        self.device = devices
        self.color_list = [
            Qt.cyan,
            Qt.magenta,
            Qt.green,
            Qt.blue,
        ]
        if not self.device[0].is_open():
            return
        self.series_data = [QLineSeries() for i in self.device]
        self.axis_y = QValueAxis()
        self.axis_x = QValueAxis()
        # self.axis_y.setRange(-5.0, 5.0)

        self.init_data()

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_data)
        self.timer.start()

    def init_data(self):
        self.chart.setAnimationOptions(QChart.AllAnimations)
        self.chart.setAnimationDuration(1)
        for dev, series, c in zip(self.device, self.series_data, self.color_list):
            ydata = dev.get_1d_array()
            # xdata = np.linspace(0, len(ydata), len(ydata))
            xdata = dev.get_x_scale()
            pen = series.pen()
            # if c is not None:
            pen.setColor(c)
            pen.setWidthF(2.5)
            series.setPen(pen)
            series.setUseOpenGL(True)
            # for x, y in zip(xdata, ydata):
            #     series.append(x, y)
            series.append(series_to_polyline(xdata, ydata))
            series.setName("%s ch%s" % (dev.get_serial(), dev.info["ch"]))

            self.chart.addSeries(series)
            self.chart.setAxisY(self.axis_y, series)
            self.chart.setAxisX(self.axis_x, series)

    def set_y_range(self, p1: float, p2: float):
        self.axis_y.setRange(p1, p2)

    def set_x_range(self, p1: float, p2: float):
        self.axis_x.setRange(p1, p2)

    def update_data(self):
        # self.clear_data()
        for series, dev in zip(self.series_data, self.device):
            ydata = dev.get_1d_array()
            # xdata = np.linspace(0, len(ydata), len(ydata))
            xdata = dev.get_x_scale()
            # series.clear()
            # for x, y in zip(xdata, ydata):
            #     series.append(x,y)
            series.replace(series_to_polyline(xdata,ydata))

