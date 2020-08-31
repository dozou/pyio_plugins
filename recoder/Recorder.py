# -*- coding:utf-8 -*-
import numpy as np
import pandas as pd
import threading
import time
from PyQt5.QtWidgets import *
from yapsy.IPlugin import IPlugin
from pyio.Main import main
from pyio.Window.LineEdit import *
from pyio.DataSturucture import *
# from pyio.System import System
from pyio.Util import System


class Viewer(QWidget):
    def __init__(self, parent=None, data_container: DataContainer = None):
        super().__init__(parent)
        self.timer = None
        self.device = data_container.device
        self.wave_data_ch1 = []
        self.wave_data_ch2 = []
        self.data_cnt = 0

        self.setWindowTitle('Record Manager')

        self.file_name_line = LabelOnLineEdit(label="FileName",
                                              text='')
        self.timeout_line = LabelOnSpinBox(label="RecordTiming",
                                           val=50.0,
                                           maximum=10000.0)
        self.size_checkbox = QCheckBox(text='記録サイズ指定')
        self.size_checkbox.stateChanged.connect(self.update_checkbox)
        self.size_line = LabelOnSpinBox(label="記録サンプル数",
                                        val=0,
                                        maximum=50000)
        self.record_button = QPushButton("記録開始")
        self.record_button.clicked.connect(self.start_record)
        self.clear_button = QPushButton("初期化")
        self.clear_button.clicked.connect(self.clear_data)
        self.write_format_checkbox = QCheckBox(text="Pkl保存")
        self.write_button = QPushButton("書き出し")
        self.write_button.clicked.connect(self.write_csv)
        self.data_cnt_text = QLabel("Samples:"+str(self.data_cnt))

        main_layout = QHBoxLayout()
        sub_layout = QVBoxLayout()
        sub_layout.addWidget(QLabel("<b>記録</b>"))
        sub_layout.addWidget(self.timeout_line)
        sub_layout.addWidget(self.size_checkbox)
        sub_layout.addWidget(self.size_line)
        sub_layout.addWidget(self.record_button)
        sub_layout.addWidget(self.clear_button)
        sub_layout.addWidget(self.write_button)
        sub_layout.addWidget(self.data_cnt_text)
        sub_layout.addWidget(self.write_format_checkbox)
        sub_layout.addWidget(self.file_name_line)
        main_layout.addLayout(sub_layout)
        self.setLayout(main_layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.rec_update)
        self.update_checkbox()
        self.check_loop = False
        self.t1 = None  # type:threading.Thread
        self.use_device = []

    def start_record(self):
        for dev in self.device:
            if dev.is_open():
                print(dev)
                self.use_device.append(dev)

        self.record_button.disconnect()
        self.record_button.setText("記録停止")
        self.record_button.clicked.connect(self.stop_record)
        self.timer.setInterval(self.timeout_line.get_value())
        if self.size_checkbox.isChecked():
            size = self.size_line.get_value()
            for i, dev in enumerate(self.use_device):
                self.wave_data_ch1.append(np.empty((size, dev.get_sample_num()), float))
                self.wave_data_ch2.append(np.empty((size, dev.get_sample_num()), float))
            print("Samples:"+str(size))
        else:
            for i, dev in enumerate(self.use_device):
                self.wave_data_ch1.append(np.empty((0, dev.get_sample_num()), float))
                self.wave_data_ch2.append(np.empty((0, dev.get_sample_num()), float))
        # self.timer.start()
        self.check_loop = True
        self.t1 = threading.Thread(target=self.__thread_func)
        self.t1.setDaemon(True)
        self.t1.start()
        self.size_checkbox.setEnabled(False)

    def stop_record(self):
        # self.timer.stop()
        self.check_loop = False
        self.record_button.disconnect()
        self.record_button.setText("記録開始")
        self.record_button.clicked.connect(self.start_record)
        self.data_cnt = 0
        self.size_checkbox.setEnabled(True)

    def update_checkbox(self):
        if self.size_checkbox.isChecked():
            self.size_line.setEnabled(True)
        else:
            self.size_line.setEnabled(False)

    def __thread_func(self):
        while self.check_loop:
            if self.size_checkbox.isChecked() and self.size_line.get_value() <= self.data_cnt:
                break
            time.sleep(self.timeout_line.get_value() / 1000.0)
            self.rec_update()
        self.stop_record()

    def rec_update(self):
        for i, dev in enumerate(self.use_device):
            data_ch1 = np.array([dev.ai_data[0]])
            data_ch2 = np.array([dev.ai_data[1]])
            if self.size_checkbox.isChecked():
                self.wave_data_ch1[i][self.data_cnt] = data_ch1[0]
                self.wave_data_ch2[i][self.data_cnt] = data_ch2[0]
                # print("ch1:"+str(len(data_ch1[0]))+" ch2:"+str(len(data_ch2[0])))
            else:
                self.wave_data_ch1[i] = np.append(self.wave_data_ch1, data_ch1, axis=0)
                self.wave_data_ch2[i] = np.append(self.wave_data_ch2, data_ch2, axis=0)
        self.data_cnt_text.setText("Samples:"+str(self.data_cnt))
        self.data_cnt += 1
        # print("data counter = %d" % self.data_cnt)

    def clear_data(self):
        self.wave_data_ch1 = []
        self.wave_data_ch2 = []
        self.data_cnt = 0

    def write_csv(self):
        system = System()
        system.load_param()
        work_dir = system.get_work_dir()
        for i, dev in enumerate(self.use_device):
            if self.write_format_checkbox.isChecked():
                wave_data = pd.DataFrame(self.wave_data_ch1[i])
                raw_file_name = self.file_name_line.get_value()
                wave_data.to_pickle(system.check_dir_str(work_dir+raw_file_name+"_dev"+str(i)+'_ch1_wave.pkl')[0])

                wave_data = pd.DataFrame(self.wave_data_ch2[i])
                raw_file_name = self.file_name_line.get_value()
                wave_data.to_pickle(system.check_dir_str(work_dir+raw_file_name+"_dev"+str(i)+'_ch2_wave.pkl')[0])
            else:
                wave_data = pd.DataFrame(self.wave_data_ch1[i])
                raw_file_name = self.file_name_line.get_value()
                wave_data.to_csv(work_dir+raw_file_name+"_dev"+str(i)+'_ch1_wave.csv')
                wave_data = pd.DataFrame(self.wave_data_ch2[i])
                raw_file_name = self.file_name_line.get_value()
                wave_data.to_csv(work_dir+raw_file_name+"_dev"+str(i)+'_ch2_wave.csv')

