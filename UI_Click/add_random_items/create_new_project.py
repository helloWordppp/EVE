# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:create_new_project.py
@className:
@Create Data:2023/9/8 9:56 14:08
@Description:
创建一个新的工程
"""
import os
import time
import traceback
import sys
import json
import random

from collections import OrderedDict

from CaseRealization.Public.logging_print import MyLogPrint
from UI_Click.EditMainUI.EditMainUI import CEditMainUI
from UI_Click.ProjectMainUI.ProjectMain import CProjectMain
from CaseRealization.Public.eve_base import CEVEBase


class CCreateNewProject(object):
    """
    创建一个新的工程
    """
    def __int__(self):
        # self.project_main = CProjectMain()
        # self.edit_main = CEditMainUI()
        pass

    def creat_one_project(self):
        """
        创建一个新的工程
        :return:
        """
        my_base_eve = CEVEBase()
        pid = my_base_eve.get_pid_by_name("VideoEditorQt.exe")

        app_path = my_base_eve.get_app_install("EaseUS VideoEditor 1.0.0")
        app_path = os.path.join(app_path, "bin", "VideoEditorQt.exe")
        # 如果程序存在则杀掉程序然后在启动
        if pid is not None:
            my_base_eve.kill_app("VideoEditorQt.exe")

        my_base_eve.run_program(app_path)
        time.sleep(20)

        # 初始化程序主界面
        project_main = CProjectMain()
        project_main.click_creat_new_project()

        time.sleep(10)

        return True


if __name__ == '__main__':
    test = CCreateNewProject()
    test.creat_one_project()