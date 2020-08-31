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
from recoder_v1.DataDevice import DataDevice

import pyperclip as clip


class Viewer(QWidget):
    def __init__(self, parent=None, data_container: DataContainer = None):
        """
        初期化
        """
        super().__init__(parent)

        self.data = data_container

        self.ai_device = []
        self.rec_device = []
        self.wave_data = []
        self.data_cnt = 0
        self.size_top = self.data_cnt
        self.data_path = ""
        self.loop_flag = False
        self.t_start = None
        self.t_end = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_record)

        # 色々描画してるところだよ
        self.setWindowTitle('Record Manager')

        self.path_line = LabelOnLineEdit(label="Path",
                                         text='')
        self.path_line_copy_button = QPushButton("📋 ")
        self.path_line_copy_button.clicked.connect(self.path_line_copy)
        self.file_name_line = LabelOnLineEdit(label="FileName",
                                              text='')
        self.timeout_line = LabelOnSpinBox(label="RecordTiming",
                                           val=50.0,
                                           maximum=10000.0)
        self.size_checkbox = QCheckBox('記録サイズ指定')
        self.size_checkbox.stateChanged.connect(self.update_checkbox)
        self.size_line = LabelOnSpinBox(label="記録サンプル数",
                                        val=100,
                                        maximum=50000)
        self.record_button = QPushButton("記録開始")
        self.record_button.clicked.connect(self.start_record)
        self.clear_button = QPushButton("初期化")
        self.clear_button.clicked.connect(self.clear_data)
        self.write_format_checkbox = QCheckBox("Pkl保存")
        self.write_format_checkbox.toggle()
        self.write_button = QPushButton("書き出し")
        self.write_button.clicked.connect(self.write_files)
        self.data_cnt_label = QLabel("")
        self.error_message_label = QLabel("")
        self.error_message_label.setStyleSheet("background:#000000; color:red;")
        self.write_checkbox = []

    def window_create(self):
        """
        pyio_v1上recorder_v1ボタン初回クリック時呼び出し関数
        """
        print("--- Connected Device(s) ---\n", self.data.device)
        for dev in self.data.device:
            if dev.info['type'] == 'ai':
                self.ai_device.append(dev)
        print("--- Found AnalogIn Device(s) ---\n", self.ai_device)
        if len(self.ai_device) == 0:
            # 標準出力
            sys.stderr.write("!! AnalogIn Device Not Found. !!\n")
            sys.stderr.write("Recoder_v1 -> Exit\n")
            return

        for i, dev in enumerate(self.ai_device):
            box_text = " " + str(dev.info['name']) + " " + str(int(dev.info['ch']) + 1) + "ch"
            self.write_checkbox.append(QCheckBox(box_text))

        # ボタンを押してから描画
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(QLabel("<b>記録</b>"))
        grid.addWidget(self.timeout_line, 1, 0)
        grid.addWidget(self.size_checkbox, 2, 0)
        grid.addWidget(self.size_line, 3, 0)
        grid.addWidget(self.record_button, 4, 0)
        grid.addWidget(self.clear_button, 5, 0)
        grid.addWidget(self.write_button, 6, 0)
        grid.addWidget(self.data_cnt_label, 7, 0)
        grid.addWidget(self.write_format_checkbox, 8, 0)
        grid.addWidget(self.path_line, 9, 0)
        grid.addWidget(self.path_line_copy_button, 9, 1)
        grid.addWidget(self.file_name_line, 10, 0)
        grid.addWidget(self.error_message_label, 11, 0)

        grid.addWidget(QLabel("--- Record Device Select ---"), 0, 2)
        for i in range(len(self.ai_device)):
            grid.addWidget(self.write_checkbox[i], (1+i), 2)

        self.setLayout(grid)

    def window_init(self):
        """
        pyio_v1上のrecoder_v1ボタンクリック時呼び出し関数
        初期化のため関数呼び出し
        """
        self.update_checkbox()
        self.update_data_cnt_label()
        self.path_setting()
        self.path_line.set_value(self.data_path)

    def update_checkbox(self):
        """
        self.size_checkboxクリック時呼び出し関数
        """
        if self.size_checkbox.isChecked():
            self.size_line.setEnabled(True)
        else:
            self.size_line.setEnabled(False)

    def start_record(self):
        """
        self.record_buttonクリック時呼び出し関数
        開始用
        """
        self.error_message_label.setText("")
        self.size_top = self.size_line.get_value()

        # 記録するデバイスリスト(self.rec_device)を作成
        self.rec_device = []
        for i, dev in enumerate(self.ai_device):
            self.write_checkbox[i].setEnabled(False)
            if self.write_checkbox[i].isChecked():
                self.rec_device.append(dev)


        # self.rec_deviceが空ではないことを確認
        if len(self.rec_device) == 0:
            # 標準出力
            sys.stderr.write("!! No Record Device. !!\n")
            self.error_message_label.setText("!! No Record Device. !!")
            return

        # self.wave_dataにself.rec_deviceの要素分の配列を追加
        for i, dev in enumerate(self.rec_device):
            if self.size_checkbox.isChecked():
                self.wave_data.append(np.empty((self.size_top, len(dev.get_1d_array())), dtype=float))

            else:
                self.wave_data.append([])

            print("self.wave_data["+str(i)+"].shape :", np.array(self.wave_data[i]).shape)

        self.record_button.setText("記録停止")
        self.re_connect(self.record_button.clicked, self.stop_record)
        # self.record_button.clicked.connect(self.stop_record)
        self.clear_button.setEnabled(False)
        self.size_checkbox.setEnabled(False)

        self.timer.setInterval(self.timeout_line.get_value())
        self.loop_flag = True
        if self.data_cnt == 0:
            self.t_start = time.time()
        self.timer.start()

    def update_record(self):
        """
        データ取得時呼び出し関数
        """
        if self.size_checkbox.isChecked():
            for i, dev in enumerate(self.rec_device):
                self.wave_data[i][self.data_cnt] = dev.get_1d_array()

        else:
            for i, dev in enumerate(self.rec_device):
                self.wave_data[i].append(dev.get_1d_array())

        self.data_cnt += 1
        self.update_data_cnt_label()
        if self.data_cnt == self.size_top:
            self.stop_record()

    def stop_record(self):
        """
        self.record_buttonクリック時呼び出し関数
        停止用
        """
        self.loop_flag = False
        self.timer.stop()
        self.t_end = time.time()
        self.record_button.setText("記録開始")
        self.re_connect(self.record_button.clicked, self.start_record)
        # self.record_button.clicked.connect(self.start_record)
        self.clear_button.setEnabled(True)
        print("--- Stop Record ---")
        print("Time :", (self.t_end - self.t_start), "[sec]")
        for i, dev in enumerate(self.rec_device):
            print("wave_data " + str(i) + " : " + dev.info['name'] + "_" + str(dev.info['id']) + " Ch:"
                  + str(dev.info['ch']) + str(np.array(self.wave_data[i]).shape))
        # print(np.array(self.wave_data).shape)

    def clear_data(self):
        """
        self.clear_buttonクリック時呼び出し関数
        記録用変数等初期化
        """
        self.loop_flag = False
        self.wave_data = []
        self.data_cnt = 0
        self.size_top = self.data_cnt
        self.update_data_cnt_label()
        self.size_checkbox.setEnabled(True)
        for i in range(len(self.ai_device)):
            self.write_checkbox[i].setEnabled(True)

    def write_files(self):
        """
        ファイル書き出し
        self.write_buttonクリック時呼び出し関数
        """
        file_path = self.path_line.get_value()
        file_name = self.file_name_line.get_value()
        print("--- Write File ---")
        if not (file_path[-1:] == "/"):
            # 標準出力
            sys.stderr.write("!! Path Error(missing \"/\") : " + str(file_path) + "\n")
            self.error_message_label.setText("!! Path Error(missing \"/\") !!")
            return
        else:
            self.error_message_label.setText("")
        print("Write file : " + file_path + file_name + "*")

        # pkl保存にチェックが入っているとき
        if self.write_format_checkbox.isChecked():
            print("Format     : " + ".pkl")
            for i, dev in enumerate(self.rec_device):
                device_text = "_" + str(dev.info['name']) + "_ch" + str(int(dev.info['ch']) + 1)

                write_data = pd.DataFrame(self.wave_data[i])
                write_data.to_pickle(file_path + file_name + device_text + "_wave.pkl")
        # 選択されていない時(csv保存)
        else:
            print("Format     : " + ".csv")
            for i, dev in enumerate(self.rec_device):
                device_text = "_" + str(dev.info['name']) + "_ch" + str(int(dev.info['ch']) + 1)

                write_data = pd.DataFrame(self.wave_data[i])
                write_data.to_csv(file_path + file_name + device_text + "_wave.csv")

    def update_data_cnt_label(self):
        """
        self.data_cnt_labelのtext更新関数
        """
        self.data_cnt_label.setText("Samples:"+str(self.data_cnt))

    def path_setting(self):
        """
        書き出し先パス設定関数
        self.data_pathにパスを代入。

        Notes
        -----
        ~/.pyio/param.json内から確認
        優先順位
        1. work_folder内設定
        2. plugin_folder内設定
        3. Homeパス
        いずれも確認できない場合はErrorメッセージをprint出力等した上で
        self.data_path=""とする。
        """
        # ~/.pyio/param.jsonの内容を取得するためpyio.UtilのSystem呼び出し
        system = System()
        system.load_param()
        # 初期値1 : param.jsonのwork_folder
        work_dir = system.get_work_dir()
        # print("work_dir : ", work_dir, " | type : ", type(work_dir))

        # 初期値2 : ~/.pyio/param.jsonのplugin_folder(複数指定の場合は必ずFalseになる)
        if not (os.path.exists(work_dir)):
            work_dir = str(system.get_pulgin_dir())
            # print("work_dir : ", work_dir, " | type : ", type(work_dir))

        # 初期値3 : ~ (Home)
        if not (os.path.exists(work_dir)):
            work_dir = str(os.path.expanduser('~'))
            # print("work_dir : ", work_dir, " | type : ", type(work_dir))

        # 初期値4 : (空)
        if not (os.path.exists(work_dir)):
            work_dir = ""
            # 標準出力
            sys.stderr.write("!Error : All default path not exists. Please type path yourself.\n")
            self.error_message_label.setText("!! Please Type Path !!")

        self.data_path = work_dir + "/"
        print("Path : " + str(self.data_path))

    def path_line_copy(self):
        """
        self.path_line_copy_buttonクリック時呼び出し関数
        self.path_lineのtextをクリップボードへコピー
        """
        copy_path = self.path_line.get_value()
        clip.copy(copy_path)

    def re_connect(self, signal, new_handler=None, old_handler=None):
        """
        Button.connect等付け替え用
        """
        while True:
            try:
                if old_handler is not None:
                    signal.disconnect(old_handler)
                else:
                    signal.disconnect()
            except TypeError:
                break
        if new_handler is not None:
            signal.connect(new_handler)

    def get_data(self):
        """
        記録されているデータを返却する
        扱いやすくするため DataDevice型に一回変換を行いDeviceManagerで纏めて返却
        """
        manager = DeviceManager()
        for i, d in enumerate(self.rec_device):  # type:(int, IODevice)
            dev = DataDevice(name=d.info['name'],type="2d_data",data=self.wave_data[i])
            manager.append(dev)

        return manager

    def get_device(self):
        """
        記録に使用したデバイスを返却する
        :return: DeviceManager
        """
        manager = DeviceManager()
        for i in self.rec_device:
            manager.append(i)
        return manager
