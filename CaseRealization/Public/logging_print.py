# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:logging_print.py
@className:
@time:2019/1/29 12:25
@function:

"""
import logging
import traceback
import time
import sys
import os
from multiprocessing import Queue


class MyLogPrint:
    """
    日柱输出类
    """
    def __init__(self, file, name=None, my_queue=None):
        """
        初始化日志输出对象
        :param file: 文件路径 str
        :param name: __name__
        """
        self.file = file
        self.logger = None
        self.name = name
        self.get_logger()
        self.my_queue = my_queue

    def print_info(self, *args):
        """
            输出日志信息，级别是info
        """
        used_line = self.pb_get_line()
        print_str = used_line + "--"
        try:
            for item in args:
                print_str += str(item) + "  "
            self.logger.info(print_str)
            if self.my_queue:
                self.my_queue.put(print_str)
        except Exception:
            for item in args:
                self.logger.info(item)
            self.logger.info("---------------MyLogPrint.print_info error info-------------------")
            self.logger.exception(Exception)
            self.logger.info("------------------------------------------------------------------")

    def print_warning(self, *args):
        """
            输出日志信息，级别是warning
        """
        used_line = self.pb_get_line()
        print_str = used_line + "--"
        try:
            for item in args:
                print_str += str(item) + "  "
            self.logger.warning(print_str)
            if self.my_queue:
                self.my_queue.put(print_str)
        except Exception:
            for item in args:
                self.logger.warning(item)
            self.logger.info("---------------MyLogPrint.print_info error info-------------------")
            self.logger.exception(Exception)
            self.logger.info("------------------------------------------------------------------")

    def print_error(self, *args):
        """
            输出日志信息，级别是error
        """
        used_line = self.pb_get_line()
        print_str = used_line + "--"
        try:
            for item in args:
                print_str += str(item) + "  "
            self.logger.error(print_str)
            if self.my_queue:
                self.my_queue.put(print_str)
        except Exception:
            for item in args:
                self.logger.error(item)
            self.logger.info("---------------MyLogPrint.print_info error info-------------------")
            self.logger.exception(Exception)
            self.logger.info("------------------------------------------------------------------")

    def print_debug(self, *args):
        """
            输出日志信息，级别是debug
        """
        used_line = self.pb_get_line()
        print_str = used_line + "--"
        try:
            for item in args:
                print_str += str(item) + "  "
            self.logger.debug(print_str)
            if self.my_queue:
                self.my_queue.put(print_str)
        except Exception:
            for item in args:
                self.logger.debug(item)
            self.logger.info("---------------MyLogPrint.print_info error info-------------------")
            self.logger.exception(Exception)
            self.logger.info("------------------------------------------------------------------")

    def get_logger(self):
        """
            获取日志输出对象
        """
        logger = logging.getLogger(self.name)

        handlers_list = logger.handlers
        has_StreamHandler = False
        for item in handlers_list:
            # print(isinstance(item, logging.FileHandler))
            if isinstance(item, logging.FileHandler):
                # print(os.path.splitext(item.baseFilename)[1].upper())
                # print(os.path.splitext(self.file)[1].upper())
                if os.path.splitext(item.baseFilename)[1].upper() == os.path.splitext(self.file)[1].upper():
                    self.logger = logger
                    return
            if isinstance(item, logging.StreamHandler):
                has_StreamHandler = True
            # logger.removeHandler(item)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 向日志中添加FileHandler 主要是文件对象，输出到文件中
        handler = logging.FileHandler(self.file, encoding="utf-8")
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # 向日志中添加StreamHandler 主要是用户控制台打印
        if not has_StreamHandler:
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            console.setLevel(logging.INFO)
            logger.addHandler(console)

        logger.setLevel(level=logging.INFO)
        self.logger = logger

    def __uninit__(self):
        """
        logger反初始化
        :return:
        """
        handlers_list = self.logger.handlers
        # print(handlers_list)
        for item in handlers_list:
            self.logger.removeHandler(item)

    def pb_get_line(self):
        """
        获取调用者的函数名称和行号
        :return:
        """
        used_line = ""
        try:
            func_name = sys._getframe().f_code.co_name
            try:
                raise Exception
            except:
                line_info = (traceback.format_stack())
            center_index = -1
            for index, item in enumerate(line_info):
                temp_list = item.split("\n")
                if temp_list.__len__() >= 2 and func_name in temp_list[1]:
                    center_index = index
            if center_index == -1:
                center_index = -2
            # used_line = line_info[center_index-1].split(func_name)[0].replace("\n", "")
            used_line = line_info[center_index - 1].split(func_name)[0].split("\n")[0]
        except:
            print(traceback.format_exc())
        return used_line


def pb_get_line():
    """
    获取调用者的函数名称和行号
    :return:
    """
    used_line = ""
    try:
        func_name = sys._getframe().f_code.co_name
        try:
            raise Exception
        except:
            line_info = (traceback.format_stack())
        center_index = -1
        print(line_info)
        for index, item in enumerate(line_info):
            temp_list = item.split("\n")
            if temp_list.__len__() >= 2 and func_name in temp_list[1]:
                center_index = index
        print(used_line)
        if used_line == -1:
            used_line = -2
        # used_line = line_info[center_index].split(func_name)[0].replace("\n", "")
        used_line = line_info[center_index - 1].split(func_name)[0].replace("\n")[0]
    except:
        print(traceback.format_exc())
    return used_line


if __name__ == '__main__':
    # file_handle = r"D:\My_temp\1231231.log"
    # file_handle1 = r"D:\My_temp\1231231_11.log"
    # test = MyLogPrint(file_handle, __name__)
    # test1 = MyLogPrint(file_handle1, __name__)
    # test_bb()
    # print(ss.f_back.f_code.co_name)

    for i in range(0, 5):
        file_handle = r"D:\My_temp\1231231.log"
        test = MyLogPrint(file_handle, __name__)
        a = ["sds"]
        # while True:
        test.print_info("sds", "asda", "vfvf", a, test, i)
        # test1.print_info("sds1", "asda1", "vfvf1", a, test1, i)
        time.sleep(1)


