# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:run_case.py
@className:
@Create Data:2023/9/11 17:33 14:08
@Description:

"""
import os
import time
import traceback
import sys
import json
import random
from copy import deepcopy

from collections import OrderedDict

from CaseRealization.Public.logging_print import MyLogPrint
from CaseRealization.Public.IniRead import CIniConfig
from UI_Click.EditMainUI.EditMainUI import CEditMainUI
from UI_Click.ProjectMainUI.ProjectMain import CProjectMain
from CaseRealization.Public.eve_base import CEVEBase
from UI_Click.add_random_items.add_random_item import CAddRandomItem
from UI_Click.add_random_items.move_random_item import CMoveRandomItem
from UI_Click.add_random_items.create_new_project import CCreateNewProject


class CRunCase(object):
    """
    运行用例
    """
    def __int__(self, my_log=None):
        self.dir_path, _ = os.path.split(sys.argv[0])
        if my_log is None:
            self.log_path = os.path.join(self.dir_path, "result", "log", "CRunCase.log")
            if not os.path.exists(os.path.split(self.log_path)[0]):
                os.makedirs(os.path.split(self.log_path)[0])
            self.log_path = os.path.join(self.dir_path, "result", "log", "CRunCase.log")
            self.my_log = MyLogPrint(self.log_path)
        else:
            self.my_log = my_log

    def run_one_case(self, cas_file_path):
        """
        运行单个用例
        :param cas_file_path:
        :return:
        """
        case_info = self.read_case_file(cas_file_path)
        case_main = CEditMainUI()
        for one_setup in case_info:
            function_name = one_setup["function_name"]
            function_pb = getattr(case_main, function_name)
            function_pb()
    def read_case_file(self, cas_file_path):
        """
        读取用例文件
        :param cas_file_path:
        :return:
        """
        case_info = []

        my_ini = CIniConfig(cas_file_path)
        my_ini.Get_data()

        all_section = my_ini.all_data.keys()

        for section in all_section:
            one_setup = OrderedDict()
            one_setup["function_name"] = my_ini.all_data[section]["function_name"]
            key_list = my_ini.all_data[section].keys()
            for key in key_list:
                if not key.startswith("argv_"):
                    continue
                one_setup[key.replace("argv_", "")] = my_ini.all_data[section][key]
            case_info.append(deepcopy(one_setup))

        return case_info


