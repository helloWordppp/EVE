# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:ProjectMain.py
@className:
@Create Data:2023/9/6 8:52 14:08
@Description:

"""
import os
import time
import traceback
import sys
import json

from collections import OrderedDict

from CaseRealization.Public.logging_print import MyLogPrint
from UI_Click.UIBase import CUIBase


class CProjectMain(CUIBase):
    def __init__(self, time_out=60, my_log=None):
        """
        初始化
        :param window_name: 窗口的 Name
        :param window_classname: 窗口的 ClassName
        AutomationId: mainpage
        """
        self.dir_path, _ = os.path.split(sys.argv[0])
        if my_log is None:
            self.log_path = os.path.join(self.dir_path, "result", "log", "CProjectMain.log")
            if not os.path.exists(os.path.split(self.log_path)[0]):
                os.makedirs(os.path.split(self.log_path)[0])
            self.log_path = os.path.join(self.dir_path, "result", "log", "CProjectMain.log")
            self.my_log = MyLogPrint(self.log_path)
        else:
            self.my_log = my_log
        window_name, window_classname = "Video Editor", "QWidget"
        super(CProjectMain, self).__init__(window_name, window_classname, time_out=time_out, my_log=self.my_log)

        self.main_product = self.get_project_main_ui(time_out)

        if self.main_product is None:
            raise Exception("主程序窗口未找到，无法进行后续流程")

        self.main_product.SetTopmost(True)

    def click_creat_new_project(self):
        """
        点击创建新项目
        :return:
        """
        child_all = self.main_product.GetChildren()
        for item in child_all:
            print(item.ControlTypeName)
            #  and item.ControlTypeName == "ButtonControl" and item.ClassName == "CIconButton"
            if item.Name == "Let's create new Video":
                item.Click()
                return True
        return False


if __name__ == '__main__':

    test = CProjectMain()
    test.click_creat_new_project()

