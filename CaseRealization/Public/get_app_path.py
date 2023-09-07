# -*- coding:utf-8 -*-

"""
@author:Pengbo
@file:get_app_path.py
@className:
@time:2019/5/29 11:17
@function:
获取本机安装的应用位置
"""

import winreg
from collections import OrderedDict
from CaseRealization.Public.get_system_info import CGet_system_info


APP_INSTALL_REGEDIT_KEY = [r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
                           r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"]
HKEY_LOCAL_MACHINE = winreg.HKEY_LOCAL_MACHINE
HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER


class CRead_regedit:
    """读取注册表"""
    def __init__(self):
        """初始化获取计算机操作系统位数"""
        system_info = CGet_system_info()
        self.system_bite = system_info.Get_system_bite()

    def Get_all_child_key(self, key, sub_key):
        """获取一个键的所有子健和子健的键值"""
        return_data = OrderedDict()
        # key_obj = winreg.OpenKey(key, sub_key, 0, winreg.KEY_WOW64_64KEY | winreg.KEY_READ )
        try:
            # 区分64位还是32位系统 调用不同的读取方式
            if int(self.system_bite) == 64:
                key_obj = winreg.OpenKey(key, sub_key, 0, winreg.KEY_WOW64_64KEY | winreg.KEY_READ)
            else:
                key_obj = winreg.OpenKey(key, sub_key, 0, winreg.KEY_WOW64_32KEY | winreg.KEY_READ)
        except:
            return return_data
        index = 0
        all_child_key = []
        # 获取键中子健(不包括 子健的子健)
        while True:
            try:
                child_key = winreg.EnumKey(key_obj, index)
                all_child_key.append(child_key)
                index += 1
            except WindowsError:
                key_obj.Close()
                break

        for item in all_child_key:
            child_sub_key = sub_key + "\\" + item
            # 区分64位还是32位系统 调用不同的读取方式
            if int(self.system_bite) == 64:
                key_obj = winreg.OpenKey(key, child_sub_key, 0, winreg.KEY_WOW64_64KEY | winreg.KEY_READ)
            else:
                key_obj = winreg.OpenKey(key, child_sub_key, 0, winreg.KEY_WOW64_32KEY | winreg.KEY_READ)
            index = 0
            enum_value = {}
            # 获取键中的所有值 不包括 data_type
            while True:
                try:
                    name, value, type = winreg.EnumValue(key_obj, index)
                    # print(name, value, type)
                    enum_value[name] = value
                    # enum_value["value"] = value
                    # enum_value["type"] = type
                    index += 1
                except WindowsError:
                    key_obj.Close()
                    break
            return_data[item] = enum_value

        return return_data

    def Get_all_app(self):
        """获取所有的本机app
            :return 字典 key为app的注册表注册表 键  值为字典 注册表中的检核值
        """
        key_list = [HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER]
        all_app = OrderedDict()
        for key in key_list:
            for sub_key in APP_INSTALL_REGEDIT_KEY:
                temp_app = self.Get_all_child_key(key, sub_key)
                # print(temp_app.__len__())
                if temp_app:
                    for app in temp_app.keys():
                        all_app[app] = temp_app[app]
        return all_app

    def Get_app_info(self, app_name):
        """
        获取某一应用的注册表信息
        :param app_name:
        :return:
        """
        all_app = self.Get_all_app()
        print(len(all_app))
        app_info = OrderedDict()
        for item in all_app.keys():
            if "DisplayName" not in all_app[item].keys():
                continue
            if app_name.lower() in all_app[item]["DisplayName"].lower():
                print("item,", item)
                app_info = all_app[item]
        # print(app_info)
        return app_info


if __name__ == '__main__':
    test = CRead_regedit()
    # ss = test.Get_all_child_key(HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    # print(ss)
    # all_app = test.Get_all_app()
    # print(all_app.__len__())
    print(test.Get_app_info("EaseUS RecExperts-test 1.0"))
