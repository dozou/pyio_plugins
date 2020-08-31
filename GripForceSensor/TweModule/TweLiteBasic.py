#!/usr/bin/python
#coding:utf-8
from PyQt5.QtChart import *
from pybration.Devices.IODevice import IODevice
from serial import *
from sys import stdout, stdin, stderr, exit
import threading
import numpy as np
import pandas as pd


class TweIO:
    def __init__(self):
        self.serial_no = "Not Serial"
        self.ao = [-1.0]*4
        self.ai = [-1.0]*4
        self.di = [-1.0]*4
        self.do = [-1.0]*4
        self.vin = -1.0

    def print(self):
        print("Serial_No=%s" % self.serial_no)
        print("AI1=%d AI2=%d AI3=%d AI4=%d" % (self.ai[0], self.ai[1], self.ai[2], self.ai[3]))
        print("DI1=%d DI2=%d DI3=%d DI4=%d" % (self.di[0], self.di[1], self.di[2], self.di[3]))


class TweLiteBasic(IODevice):
    def __init__(self, device_adress):
        super().__init__()
        self.ser = Serial(device_adress, 115200, timeout=0.1)
        self.check_loop = True
        self.device_io = TweIO()
        self.t1 = None

    def start(self):
        self.check_loop = True
        self.t1 = threading.Thread(target=self.loop_process)
        self.t1.setDaemon(True)
        self.t1.start()

    def stop(self):
        self.check_loop = False
        time.sleep(0.5)

    def loop_process(self):
        while self.check_loop:
            line = self.ser.readline().rstrip()  # １ライン単位で読み出し、末尾の改行コードを削除（ブロッキング読み出し）

            b_command = False
            b_str = False

            if len(line) > 0:
                c = line[0]
                if isinstance(c, str):
                    if c == ':': b_command = True
                    b_str = True
                else:
                    # python3 では bytes 型になる
                    if c == 58: b_command = True

                # print("\n%s" % line)

            if not b_command:
                continue

            try:
                lst = {}

                # for Python3
                import codecs
                s = line[1:].decode("ascii")  # bytes -> str 変換
                lst = codecs.decode(s, "hex_codec")  # hex_codec でバイト列に変換 (bytes)

                csum = sum(lst) & 0xff  # チェックサムは 8bit 計算で全部足して　0 なら OK
                lst = lst[0:len(lst) - 1]  # チェックサムをリストから削除
                if csum == 0:
                    if lst[1] == 0x81:
                        self.parse_payload(lst)  # IO関連のデータの受信
                    else:
                        pass
                        #self.parse_payload(lst)  # その他のデータ受信
                else:
                    print("checksum ng")
            except:
                if len(line) > 0:
                    print("...skip (%s)" % line)  # エラー時

    def parse_payload(self, data):
        if len(data) != 23:
            return False  # データサイズのチェック

        ladr = data[5] << 24 | data[6] << 16 | data[7] << 8 | data[8]

        '''電源の更新'''
        self.device_io.vin = data[13] << 8 | data[14]

        '''DIの更新'''
        dibm = data[16]
        dibm_chg = data[17]
        di_chg = {}  # 一度でもLo(1)になったら1
        for i in range(1, 5):
            self.device_io.di[i-1] = 0 if (dibm & 0x1) == 0 else 1
            di_chg[i] = 0 if (dibm_chg & 0x1) == 0 else 1
            dibm >>= 1
            dibm_chg >>= 1

        '''AIの更新'''
        er = data[22]
        for i in range(1, 5):
            av = data[i + 18 - 1]
            if av == 0xFF:
                # ADポートが未使用扱い(おおむね2V以)なら -1
                self.device_io.ai[i-1] = -1
            else:
                # 補正ビットを含めた計算
                self.device_io.ai[i-1] = ((av * 4) + (er & 0x3)) * 4
            er >>= 2

    def __del__(self):
        self.stop()


if __name__ == '__main__':

    device = TweLiteBasic("/dev/tty.usbserial-MWHCYFV")
    device.start()

    while True:
        try:
            # 標準入力から１行読みだす
            l = stdin.readline().rstrip()

            if len(l) > 0:
                if l[0] == 'q':  # q を入力すると終了
                    device.stop()
                    break

                if l[0] == ':':  # :からの系列はそのままコマンドの送信
                    cmd = l + "\r\n"
                    print("--> " + l)
                    device.ser.write(cmd)
        except KeyboardInterrupt:  # Ctrl+C
            device.stop()
            exit(0)
        except SystemExit:
            exit(0)
        except:
            # 例外発生時には終了
            print("... unknown exception detected")
            break