# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:excel_write.py
@className:
@time:2019/9/24 9:42
@function:

"""

import xlsxwriter
import xlrd
import os
import logging
import traceback
from collections import OrderedDict


class CWriteResult:
    """

    """
    def __init__(self, excel_name, my_signal):
        if os.path.exists(excel_name):
            try:
                os.remove(excel_name)
            except:
                print("删除已存在的数据失败")
                raise Exception("删除已存在的数据失败")
        self.my_signal = my_signal
        self.workbook = xlsxwriter.Workbook(excel_name)
        self.excel_name = excel_name

    def Write_raw_data(self, raw_data_dir):
        """
        写原始数据，也就是数据中的数据
        :param raw_data_dir: 数据字典
        :return:
        """
        col = 0
        self.my_signal.emit(["开始导出原始数据..."])

        raw_data_sheet = self.workbook.add_worksheet("raw_data")
        for key in raw_data_dir.keys():
            raw_data_sheet.write_string(0, col, key)
            for row in range(1, len(raw_data_dir[key])+1):
                write_result = raw_data_sheet.write_string(row, col, str(raw_data_dir[key][row-1]))
                if write_result < 0:
                    print("write excel error，Write_raw_data:{0}".format(raw_data_dir[key][row]))
            col = col+1
        self.my_signal.emit(["导出原始数据完成..."])
        print("Write_raw_data finish.")

    def Write_pmonitor_data(self, pmonitor_data_dir):
        """
        写每一项的性能数据
        :param pmonitor_data_dir: 性能数据字典 字典的key为sheet名 对应的值为字典（字典中key为性能数据描述，
        value为对应的值，如{"cpu":{"max_value":20, "main_value":0}}. 特别注意key如果是“Trend_path”代表的是性
        能图片的完整路劲）
        :return:
        """
        merge_format_title = self.workbook.add_format({
            'bold': True,
            'border': 6,
            'align': 'center',  # 水平居中
            'valign': 'vcenter',  # 垂直居中
            'fg_color': '#D7E4BC',  # 颜色填充
        })

        merge_format_right = self.workbook.add_format({
            'bold': True,
            'align': 'right',  # 水平居中
            'valign': 'vcenter',  # 垂直居中
        })

        merge_format_left = self.workbook.add_format({
            'bold': True,
            'align': 'left',  # 水平居中
            'valign': 'vcenter',  # 垂直居中
        })

        for sheet_name in pmonitor_data_dir.keys():
            self.my_signal.emit(["开始导出{0}性能数据.".format(sheet_name)])
            pm_sheet = self.workbook.add_worksheet(str(sheet_name))
            # 设置第1,2,3行的高度为30像素
            for i in range(0, 8):
                pm_sheet.set_row(i, 30)
            for j in range(0, 10):
                if j%3 == 0:
                    pm_sheet.set_column(j, j, 15)
                elif j%3 == 1:
                    pm_sheet.set_column(j, j, 25)
                else:
                    pm_sheet.set_column(j, j, 10)

            title_str = "性能测试报告:{0}".format(sheet_name)
            pm_sheet.merge_range(0, 0, 1, 8, title_str, merge_format_title)

            row = 2
            col = 0
            for item in pmonitor_data_dir[sheet_name].keys():
                if item == "Trend_path":
                    continue
                pm_sheet.write_string(row, col, item, merge_format_right)
                pm_sheet.write_string(row, col+1, str(pmonitor_data_dir[sheet_name][item]), merge_format_left)
                col = col + 3
                if col >= 8:
                    row = row + 1
                    col = 0

            if "Trend_path" in pmonitor_data_dir[sheet_name].keys():
                pm_sheet.insert_image(row+2, 0, pmonitor_data_dir[sheet_name]["Trend_path"])
            self.my_signal.emit(["导出{0}性能数据完成.".format(sheet_name)])

    def Write_all_data(self, pmonitor_data_dir):
        """
        写入总的数据
        :return:
        """
        merge_format_title = self.workbook.add_format({
            'bold': True,
            'border': 6,
            'align': 'center',  # 水平居中
            'valign': 'vcenter',  # 垂直居中
            'fg_color': '#D7E4BC',  # 颜色填充
        })

        merge_format_data_title = self.workbook.add_format({
            'bold': True,
            'align': 'center',  # 水平居中
            'valign': 'vcenter',  # 垂直居中
        })

        merge_format_data = self.workbook.add_format({
            'bold': False,
            'align': 'center',  # 水平居中
            'valign': 'vcenter',  # 垂直居中
        })

        all_data_sheet = self.workbook.add_worksheet("数据总览")

        for i in range(0, 10):
            all_data_sheet.set_row(i, 30)
        all_data_sheet.set_column(0, 0, 15)
        all_data_sheet.set_column(1, 10, 20)

        title_str = "性能测试报告数据总览"
        all_data_sheet.merge_range(0, 0, 1, 8, title_str, merge_format_title)

        row = 3
        set_title = 0

        for item in pmonitor_data_dir.keys():
            if set_title == 0:
                set_title = 1
                j = 1
                for title in pmonitor_data_dir[item].keys():
                    if title == "Trend_path":
                        continue
                    all_data_sheet.write_string(2, j, title, merge_format_data_title)
                    j += 1

            all_data_sheet.write_string(row, 0, item, merge_format_data_title)
            j = 1
            for temp_key in pmonitor_data_dir[item].keys():
                if temp_key == "Trend_path":
                    continue
                all_data_sheet.write_string(row, j, str(pmonitor_data_dir[item][temp_key]), merge_format_data)
                j += 1
            row = row + 1

    def Runlogic(self, pmonitor_data_dir, raw_data_dir):
        """
        逻辑控制
        :return:
        """
        if pmonitor_data_dir:
            try:
                self.Write_all_data(pmonitor_data_dir)
                self.Write_pmonitor_data(pmonitor_data_dir)
            except:
                error = traceback.format_exc()
                self.my_signal.emit(["导出性能数据异常.", str(error)])
                print(error)
        else:
            self.my_signal.emit(["没有导出性能数据."])
        if raw_data_dir:
            try:
                self.Write_raw_data(raw_data_dir)
            except:
                error = traceback.format_exc()
                self.my_signal.emit(["导出原始数据异常.", str(error)])
                print(error)
        else:
            self.my_signal.emit(["没有导出原始数据."])
        self.my_signal.emit(["数据导出完成，正在生成文件."])
        self.workbook.close()
        self.my_signal.emit(["数据导出完成，结果文件位置:{0}.".format(self.excel_name)])
        print("ok")

