# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:get_capcut_source.py
@className:
@Create Data:7/24/2023 1:13 PM 14:08
@Description:

"""

import os
import time
import sys
import json
import traceback
from collections import OrderedDict
import shutil
from copy import deepcopy

from CaseRealization.Public.eve_base import CEVEBase
from UIClick.UIBase import CUIBase


class CCapcut(CEVEBase):
    def __init__(self):
        super(CCapcut, self).__init__()

    def click_all(self):
        """

        :return:
        """
        # 获取主界面handle
        handle = self.get_main_handle()
        self.set_app_top(set_top=True, hwnd=handle)
        time.sleep(1)
        # 获取界面位置左上角顶点位置
        left, top, right, bottom = self.get_window_rect(handle)

        # x = left + 248 + 75 + 175 * 0
        # y = top + 208 + 80 + 193 * 0
        # self.click_mous(x, y)
        # time.sleep(1)


        for i in range(0, 3):
            for col in range(0, 5):
                for row in range(0, 8):
                    x = left + 248 + 75+175*row
                    y = top + 208 + 80+193*col
                    self.click_mous(x, y)
                    time.sleep(1)
            self.scroll_bar_move(value=600, direction=-1)
            time.sleep(1)
        self.set_app_top(set_top=False, hwnd=handle)

    def get_main_handle(self):
        """
        获取capcut的界面句柄
        :return:
        """
        process_handle_list = self.get_app_window_hwnd(process_name="CapCut.exe", all_handle=True)

        evw_handle = 0
        max_w = 0
        max_h = 0

        for one_handle in process_handle_list:
            w, h = self.get_app_size(one_handle["hwnd"])
            # print(w, h)
            if w > max_w and h > max_h:
                evw_handle = one_handle["hwnd"]
                max_w = deepcopy(w)
                max_h = deepcopy(h)
        self.my_log.print_info("get_amin_handle hwnd is:{0} max_w:{1} max_h:{2}".format(evw_handle, max_w, max_h))

        return evw_handle


if __name__ == '__main__':
    test = CCapcut()
    test.click_all()
