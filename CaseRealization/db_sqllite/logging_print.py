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


class MyLogPrint:
    def __init__(self, file):
        self.file = file
        self.logger = self.get_logger()


    def print_info(self, *args):
        """
            输出日志信息，级别是info
        """
        print_str = ""
        try:
            for item in args:
                print_str += str(item) + "  "
            self.logger.info(print_str)
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
        print_str = ""
        try:
            for item in args:
                print_str += str(item) + "  "
            self.logger.warning(print_str)
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
        print_str = ""
        try:
            for item in args:
                print_str += str(item) + "  "
            self.logger.error(print_str)
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
        print_str = ""
        try:
            for item in args:
                print_str += str(item) + "  "
            self.logger.debug(print_str)
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
        logger = logging.getLogger(__name__)
        logger.setLevel(level=logging.DEBUG)
        handler = logging.FileHandler(self.file)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        console = logging.StreamHandler()
        console.setFormatter(formatter)
        console.setLevel(logging.DEBUG)

        logger.addHandler(handler)
        logger.addHandler(console)

        return logger

import time
if __name__ == '__main__':
    test = MyLogPrint()
    a = ["sds"]
    while True:
        test.print_info("sds", "asda", "vfvf", a, test)
        time.sleep(2)

