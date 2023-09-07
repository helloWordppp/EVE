# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:IniRead.py
@className:
@time:2019/7/8 10:29
@function:
读写INI文件（不用api）
"""

import os
import chardet
import traceback
from collections import OrderedDict
import logging


class CIniConfig:
    """
    读写ini文件
    """
    def __init__(self, ini_file_path):
        """
        初始化函数
        :param ini_file_path: ini文件的路径
        """
        self.ini_file_path = ini_file_path
        self.all_lines = []
        self.all_data = OrderedDict()

    def Get_file_code(self, path):
        """
        获取文档的编码类型，如果失败则返回none
        :param path:文件路径
        :return:文件编码
        """
        try:
            with open(path, 'rb') as file:
                data = file.read(20000)
                dicts = chardet.detect(data)
        except:
            print(traceback.format_exc())
            return None
        return dicts["encoding"]

    def Get_data(self):
        """
        获取ini文件内容
        :param ini_file_path:
        :return:None
        """
        file_code = self.Get_file_code(self.ini_file_path)

        if not os.path.exists(self.ini_file_path):
            raise Exception("file is not exists.", self.ini_file_path)
        # if os.path.getsize(self.ini_file_path) > 1024:
        #     raise Exception("文件大小超过1MB")
        print(file_code)
        if not file_code:
            file_handle = open(self.ini_file_path, "r")
        else:
            file_handle = open(self.ini_file_path, "r", encoding=file_code)

        line = file_handle.readline()
        all_lines = []
        while line:
            try:
                new_line = line.strip().replace("\n", "")
                if new_line:
                    all_lines.append(new_line)
                line = file_handle.readline()
            except:
                pass
        if file_handle:
            file_handle.close()
        self.all_lines = all_lines
        self.Get_all_section()

    def Get_all_section(self):
        """
        获取所有额section
        :return:None
        """
        all_data = OrderedDict()
        for index in range(0, len(self.all_lines)):
            line = self.all_lines[index]
            if line.endswith("]") and line.startswith("["):
                one_section = line.replace("[", "").replace("]", "")
                if not one_section:
                    continue
                one_data = OrderedDict()
                while True:
                    index = index + 1
                    if index == len(self.all_lines):
                        break
                    line = self.all_lines[index]
                    if line.endswith("]") and line.startswith("["):
                        break
                    if "=" in line:
                        temp = line.split("=")
                        value = ""
                        for i in range(1, len(temp)):
                            value += temp[i] + "="
                        value = value[:-1]
                        one_data[temp[0].strip()] = value.strip()
                all_data[one_section] = one_data
        self.all_data = all_data

    def Get_section(self, section, key):
        """
        获取某一个键值的值
        :param section:节点名
        :param key:键
        :return:节点键对应的值
        """
        if section not in self.all_data.keys():
            raise Exception("section is not exists.")
        if key not in self.all_data[section].keys():
            raise Exception("key is not exists.")
        return self.all_data[section][key]

    def Set_section(self, section, key, value):
        """
        修改ini文件
        :param section:节点名
        :param key:键
        :param value:值
        :return:None
        """
        try:
            if section not in self.all_data.keys():
                self.all_data[section] = OrderedDict()
            self.all_data[section][key] = value
            self.Update_file()
        except Exception:
            print(logging.exception(Exception))
            raise Exception("Modifying ini file failed!")

    def Update_file(self):
        """
        写ini文件
        :return:None
        """
        file_code = self.Get_file_code(self.ini_file_path)
        with open(self.ini_file_path, "w", encoding=file_code) as file_handle:
            for item in self.all_data.keys():
                new_line = "[" + item + "]" + "\n"
                file_handle.write(new_line)
                for chile_item in self.all_data[item].keys():
                    child_line = chile_item + "=" + self.all_data[item][chile_item] + "\n"
                    file_handle.write(child_line)
                file_handle.write("\n")


if __name__ == '__main__':
    test = CIniConfig(r"D:\WDR\123.ini")
    test.Get_data()
    print(test.Get_section("section_1", "key_1"))
    test.Set_section("test1", "key1", "kkk222kk")
    test.Set_section("test2", "key1", "kkkkk2")
