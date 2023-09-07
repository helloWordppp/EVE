# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:import.py
@className:
@time:2019/9/24 9:40
@function:

"""

import time
import traceback
from PyQt5.QtCore import QThread, pyqtSignal
from CaseRealization.db_sqllite.excel_write import CWriteResult
from CaseRealization.db_sqllite.select_data import CSelect_data


class CExportResult(QThread):
    """

    """
    my_signal = pyqtSignal(list)

    def __init__(self, excel_name, pmonitor_data_dir, raw_data_dir):
        """

        :param excel_name:excel文件的完整路径
        :param pmonitor_data_dir:性能数据字典参数格式查看 下面的例子
        :param raw_data_dir:原始数据字典
        """
        super(CExportResult, self).__init__()
        try:
            self.my_excel = CWriteResult(excel_name, self.my_signal)
            self.pmonitor_data_dir = pmonitor_data_dir
            self.raw_data_dir = raw_data_dir
        except:
            error = traceback.format_exc()
            print(error)
            raise Exception("初始化写结果类失败。")

    def run(self):
        """
        线程启动
        :return:
        """
        self.my_signal.emit(["开始导出数据."])
        try:
            self.my_excel.Runlogic(self.pmonitor_data_dir, self.raw_data_dir)
        except:
            error = traceback.format_exc()
            print(error)
            self.my_signal.emit(["导出数据异常.", error])


if __name__ == '__main__':
    test = CSelect_data()
    # print(test.Get_table_exist("TbService"))
    # raw_data_dir = test.Select_data("RecExperts")
    result = test.Select_data_avg("RecExperts", r"E:\MyProject\PythonProject\ERE3.5\CaseRealization\db_sqllite\DB_data\performance_data_2023-05-31_11-29-49.db")
    print(result)
    # pmonitor_data_dir = {"cpu": {"max_value": 10, "main_value": 3, "max_handle": 600, "main_handle": 500, "Trend_path": r"D:\360downloads\323638.jpg"},
    #                      "memory": {"max_value": 10, "main_value": 3, "max_handle": 600, "main_handle": 500}}
    # excel_path = r"D:\360downloads\123.xls"
    # my_thild = CExportResult(excel_path, pmonitor_data_dir, raw_data_dir)
    # my_thild.start()
    # my_thild.wait()

