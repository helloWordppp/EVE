# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:notification_thread.py
@className:
@time:2019/8/23 12:23
@function:
通知界面的线程
"""
import time
import traceback
from PyQt5.QtCore import QThread, pyqtSignal


class CNotification(QThread):
    """
    通知界面进程状态的线程，进程是否存在，是否超过警戒值
    """
    my_signal = pyqtSignal(list)

    def __init__(self):
        super(CNotification, self).__init__()
        self.q = None

    def run(self):
        while True:
            try:
                if not self.q.empty():
                    content = self.q.get(timeout=3)
                    if content:
                        # print(content)
                        self.my_signal.emit(content)
                    else:
                        time.sleep(1)
                else:
                    time.sleep(0.5)
            except:
                print(traceback.format_exc())
