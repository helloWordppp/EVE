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
import shutil

from collections import OrderedDict

from CaseRealization.Public.logging_print import MyLogPrint
from CaseRealization.Public.IniRead import CIniConfig
from UI_Click.EditMainUI.EditMainUI import CEditMainUI
from UI_Click.ProjectMainUI.ProjectMain import CProjectMain
from CaseRealization.Public.eve_base import CEVEBase
from UI_Click.add_random_items.add_random_item import CAddRandomItem
from UI_Click.add_random_items.move_random_item import CMoveRandomItem
from UI_Click.add_random_items.create_new_project import CCreateNewProject


class CRunCasePb(object):
    """
    运行用例
    """

    def __init__(self):
        self.dir_path, _ = os.path.split(sys.argv[0])

        self.log_path = os.path.join(self.dir_path, "result", "log", "CRunCase.log")
        if not os.path.exists(os.path.split(self.log_path)[0]):
            os.makedirs(os.path.split(self.log_path)[0])
        self.log_path = os.path.join(self.dir_path, "result", "log", "CRunCase.log")
        self.my_log = MyLogPrint(self.log_path)


    def run_one_case(self, cas_file_path):
        """
        运行单个用例
        :param cas_file_path:
        :return:
        """
        case_info = self.read_case_file(cas_file_path)
        case_run_result = []
        case_run_result_bool = True
        for one_setup in case_info:
            one_setup_run_result = deepcopy(one_setup)

            if not case_run_result_bool:
                one_setup_run_result["result"] = "没有执行"
                case_run_result.append(deepcopy(one_setup_run_result))
                continue

            self.my_log.print_info(one_setup)
            function_pb = None
            function_name = one_setup["function_name"]
            # 创建工程相关
            try:
                methods = [method for method in dir(CCreateNewProject) if
                           callable(getattr(CCreateNewProject, method)) and not method.startswith("__")]
                if function_name in methods:
                    case_main = CCreateNewProject()
                    function_pb = getattr(case_main, function_name)
            except:
                self.my_log.print_info(traceback.format_exc())
            # 编辑界面相关
            if function_pb is None:
                try:
                    methods = [method for method in dir(CEditMainUI) if
                               callable(getattr(CEditMainUI, method)) and not method.startswith("__")]
                    print(methods)
                    if function_name in methods:
                        case_main = CEditMainUI()
                        function_pb = getattr(case_main, function_name)
                except:
                    self.my_log.print_info(traceback.format_exc())
            if function_pb is None:
                self.my_log.print_info("用例执行失败")
                one_setup_run_result["result"] = "没有该方法"
                case_run_result_bool = False
                case_run_result.append(deepcopy(one_setup_run_result))
                continue
            try:
                one_setup.pop("setup")
                one_setup.pop("doc")
                one_setup.pop("function_name")
            except:
                self.my_log.print_info(traceback.format_exc())
                case_run_result_bool = False
                one_setup_run_result["result"] = "参数错误,用例步骤中没有 doc function_name"
            self.my_log.print_info("function_name:{0} one_setup:{1}".format(function_pb, one_setup))
            try:
                result = function_pb(**one_setup)
                self.my_log.print_info(
                    "function_name{0} one_setup:{1} result:{2}".format(function_pb, one_setup, result))
                one_setup_run_result["result"] = result
            except:
                self.my_log.print_info(traceback.format_exc())
                one_setup_run_result["result"] = "该步骤执行失败,错误信息查看日志"
                case_run_result_bool = False

            case_run_result.append(deepcopy(one_setup_run_result))

        return case_run_result

    def write_case(self, case_pat, case_run_result):
        """
        将结果写入文件中
        :param case_name: 用例名称
        :param case_run_result: 用例执行结果
        :return:
        """
        case_name = os.path.splitext(os.path.split(case_pat)[1])[0]
        case_name =  case_name + "_" + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time())) + "_.ini"
        result_cas_path = os.path.join(self.dir_path, "run_result", "case_run")
        if not os.path.exists(result_cas_path):
            os.makedirs(result_cas_path)
        case_run_result_file_path = os.path.join(result_cas_path, case_name)

        shutil.copy(case_pat, case_run_result_file_path)

        my_ini = CIniConfig(case_run_result_file_path)
        my_ini.Get_data()

        for one_setup in case_run_result:
            section = one_setup["setup"]
            for key in one_setup.keys():
                if key in ["doc", "result"]:
                    my_ini.Set_section(section, key, one_setup[key])


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
            one_setup["setup"] = section
            one_setup["function_name"] = my_ini.all_data[section]["function_name"]
            key_list = my_ini.all_data[section].keys()
            for key in key_list:
                # if not key.startswith("argv_"):
                #     continue
                one_setup[key.replace("argv_", "")] = my_ini.all_data[section][key]
            case_info.append(deepcopy(one_setup))

        return case_info

if __name__ == '__main__':
    test = CRunCasePb()
    case_run_result = test.run_one_case(r"E:\添加素材然后导入到主轨.txt")
    test.write_case(r"E:\添加素材然后导入到主轨.txt", case_run_result)
