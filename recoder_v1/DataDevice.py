# -*- coding:utf-8 -*-
import time
import os.path
import sys
import time
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import *
from yapsy.IPlugin import IPlugin
from pyio.Main import main
from pyio.Util import System
from pyio.Window.LineEdit import *
from pyio.DataSturucture import *
from pyio.Devices.IODevice import IODevice


class DataDevice(IODevice):

    def __init__(self, name, type, data):
        super(DataDevice, self).__init__()
        self.info['name'] = name
        self.info['type'] = type
        self.data = data

    def open_device(self) -> bool:
        return True

    def close_device(self) -> bool:
        return True

    def is_open(self) -> bool:
        return True

    def get_2d_array(self):
        return self.data
