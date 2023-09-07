# -*- coding:utf-8 -*-

"""
@author:Pengbo
@file:write_result.py
@className:
@time:2019/2/20 13:08
@function:

"""
from collections import OrderedDict
import os
import sys
import time
import shutil
import xlrd
# import openpyxl
import traceback
import xlsxwriter


class CWriteExcel:
    """读写excel"""
    def __init__(self):
        pass

    def Write_excel(self, file_path, data, sheet_name):
        """
        写文件
        :param file_path: 文件路劲
        :param data: 要写入的数据（字典类型，key为列名，value为值）
        :param sheet_name: 写入到那个表格中
        :return: None
        """
        file_data = OrderedDict()
        if os.path.exists(file_path):
            file_data = self.Get_excel_dat(file_path)
            # 判断需要新建的表是否存在与原文件中
            if sheet_name in file_data.keys():
                # 表中是否
                if file_data[sheet_name] and len(file_data[sheet_name]) > 0:
                    # 判断现有的key是否和已经存在的key是一致的
                    if file_data[sheet_name][0].keys() == data.keys():
                        file_data[sheet_name].append(data)
                    else:
                        # 处理以前的数据，如果新添加的列不在以前列中时添加一列并设置为空
                        temp_add = OrderedDict()
                        for index, data_key in enumerate(data.keys()):
                            if data_key not in file_data[sheet_name][0].keys():
                                temp_add[data_key] = data[data_key]
                        for index, item in enumerate(file_data[sheet_name]):
                            for key in temp_add.keys():
                                file_data[sheet_name][index][key] = ""
                        # 处理新增的数据，如果新增的数据以前的列不存在则添加
                        temp = OrderedDict()
                        for key in file_data[sheet_name][0].keys():
                            temp[key] = ""
                        for data_key in data.keys():
                            temp[data_key] = data[data_key]
                        file_data[sheet_name].append(temp)
                else:
                    file_data[sheet_name].append(data)  # 添加新表
            else:
                file_data[sheet_name] = [data]
        else:
            file_data[sheet_name] = [data]

        workbook = xlsxwriter.Workbook(file_path)
        for sheet in file_data.keys():
            mysheet = workbook.add_worksheet(sheet)
            mysheet.set_row(0, 30)

            for index, item in enumerate(file_data[sheet][0].keys()):
                mysheet.write(0, index, item)
            for row, one_row in enumerate(file_data[sheet]):
                mysheet.set_row(row+1, 25)
                for col, key in enumerate(one_row.keys()):
                    if "result" in key:
                        mysheet.set_column(col, col, 30)
                    else:
                        mysheet.set_column(col, col, 20)
                    mysheet.write(row+1, col, one_row[key])
        workbook.close()

    def Write_excel_list(self, file_path, data_list, sheet_name):
        file_data = OrderedDict()
        if os.path.exists(file_path):
            file_data = self.Get_excel_dat(file_path)
            # 判断需要新建的表是否存在与原文件中
            if sheet_name in file_data.keys():
                # 表中是否
                if file_data[sheet_name] and len(file_data[sheet_name]) > 0:
                    # 判断现有的key是否和已经存在的key是一致的
                    for data in data_list:
                        if file_data[sheet_name][0].keys() == data.keys():
                            file_data[sheet_name].append(data)
                        else:
                            # 处理以前的数据，如果新添加的列不在以前列中时添加一列并设置为空
                            temp_add = OrderedDict()
                            for index, data_key in enumerate(data.keys()):
                                if data_key not in file_data[sheet_name][0].keys():
                                    temp_add[data_key] = data[data_key]
                            for index, item in enumerate(file_data[sheet_name]):
                                for key in temp_add.keys():
                                    file_data[sheet_name][index][key] = ""
                            # 处理新增的数据，如果新增的数据以前的列不存在则添加
                            temp = OrderedDict()
                            for key in file_data[sheet_name][0].keys():
                                temp[key] = ""
                            for data_key in data.keys():
                                temp[data_key] = data[data_key]
                            file_data[sheet_name].append(temp)
                else:
                    for data in data_list:
                        file_data[sheet_name].append(data)  # 添加新表
            else:
                file_data[sheet_name] = data_list
        else:
                file_data[sheet_name] = data_list

        workbook = xlsxwriter.Workbook(file_path)
        for sheet in file_data.keys():
            mysheet = workbook.add_worksheet(sheet)
            mysheet.set_row(0, 30)
            for index, item in enumerate(file_data[sheet][0].keys()):
                mysheet.write(0, index, item)
            for row, one_row in enumerate(file_data[sheet]):
                mysheet.set_row(row + 1, 25)
                for col, key in enumerate(one_row.keys()):
                    if "result" in key:
                        mysheet.set_column(col, col, 30)
                    else:
                        mysheet.set_column(col, col, 20)
                    if "dmp_log_path" in key or "user_operation" in key:
                        # print("-----", one_row[key])
                        mysheet.write_url(row + 1, col, one_row[key], string=key)
                        continue
                    mysheet.write(row + 1, col, one_row[key])
        workbook.close()

    def Get_excel_dat(self, file_path):
        """
        获取excel文件数据
        :param file_path: 文件路径
        :return: file_data字典类型的数据
        """
        file_data = OrderedDict()
        workbook = xlrd.open_workbook(file_path)
        sheets = workbook.sheets()

        for sheet in sheets:
            sheet_data = []
            for row in range(1, sheet.nrows):
                temp_dir = OrderedDict()
                for col in range(0, sheet.ncols):
                    temp_dir[sheet.cell(0, col).value] = str(sheet.cell(row, col).value)
                sheet_data.append(temp_dir)
            file_data[sheet.name] = sheet_data

        return file_data

    def Get_excel_data_list(self, file_path):
        """
        获取excel数据，返回OrderedDict(sheet_name,list)
        :param file_path:
        :return:
        """
        file_data = OrderedDict()
        workbook = xlrd.open_workbook(file_path)
        sheets = workbook.sheets()

        for sheet in sheets:
            sheet_data = []
            for row in range(1, sheet.nrows):
                temp_dir = []
                for col in range(0, sheet.ncols):
                    temp_dir.append(str(sheet.cell(row, col).value))
                sheet_data.append(temp_dir)
            file_data[sheet.name] = sheet_data

        return file_data

    def Write_excel_list_dir(self, file_path, data, sheet_name, trend_dir=OrderedDict()):
        """
        写文件
        :param file_path: 文件路劲
        :param data: 格式是list  list里面是字典
        :param sheet_name: 写入到那个表格中
        :param trend_dir: dir {"sheet_name":"trend_path"}
        :return: None
        """
        if len(data) == 0:
            try:
                print(data)
            except:
                print(traceback.format_exc())
            return
        file_data = OrderedDict()
        if os.path.exists(file_path):
            file_data = self.Get_excel_dat(file_path)
            # 判断需要新建的表是否存在与原文件中
            if sheet_name in file_data.keys():
                # 表中是否有数据
                if file_data[sheet_name] and len(file_data[sheet_name]) > 0:
                    # 判断现有的key是否和已经存在的key是一致的
                    # if file_data[sheet_name].__len__() <= 0 or data.__len__ <= 0:
                    #
                    if file_data[sheet_name][0].keys() == data[0].keys():
                        for item in data:
                            file_data[sheet_name].append(item)
                    else:
                        # 处理以前的数据，如果新添加的列不在以前列中时添加一列并设置为空
                        temp_add = OrderedDict()
                        for index, data_key in enumerate(data[0].keys()):
                            if data_key not in file_data[sheet_name][0].keys():
                                temp_add[data_key] = data[0][data_key]
                        for index, item in enumerate(file_data[sheet_name]):
                            for key in temp_add.keys():
                                file_data[sheet_name][index][key] = ""
                        # 处理新增的数据，如果新增的数据以前的列不存在则添加
                        temp = OrderedDict()
                        for key in file_data[sheet_name][0].keys():
                            temp[key] = ""
                        for data_key in data[0].keys():
                            temp[data_key] = data[0][data_key]
                        file_data[sheet_name].append(temp)
                else:
                    for item in data:
                        file_data[sheet_name].append(item)  # 添加新表
            else:
                file_data[sheet_name] = []
                for item in data:
                    file_data[sheet_name].append(item)
        else:
            file_data[sheet_name] = []
            for item in data:
                file_data[sheet_name].append(item)

        workbook = xlsxwriter.Workbook(file_path)
        for sheet in file_data.keys():
            mysheet = workbook.add_worksheet(sheet)
            mysheet.set_row(0, 30)

            for index, item in enumerate(file_data[sheet][0].keys()):
                mysheet.write(0, index, item)
            for row, one_row in enumerate(file_data[sheet]):
                mysheet.set_row(row+1, 25)
                for col, key in enumerate(one_row.keys()):
                    if "result" in key:
                        mysheet.set_column(col, col, 30)
                    else:
                        mysheet.set_column(col, col, 20)
                    # print(one_row[key])
                    mysheet.write(row+1, col, str(one_row[key]))
            if trend_dir:
                if sheet in trend_dir.keys():
                    if ";" in trend_dir[sheet]:
                        image_num = 0
                        for item_trend_path in trend_dir[sheet].split(";"):
                            if not os.path.isfile(item_trend_path) or not os.path.exists(item_trend_path):
                                continue
                            mysheet.insert_image(3, file_data[sheet][0].keys().__len__()+1+image_num, item_trend_path)
                            image_num += 1
                    else:
                        mysheet.insert_image(3, file_data[sheet][0].keys().__len__() + 1, trend_dir[sheet])
        workbook.close()


    def Write_before(self, file_name):
        """
        写表格数据前，判断文件是否存在，如果存在则删除文件
        :param file_name: 文件名（不包含路劲）
        :return: excel文件完整路劲（当前目录下的/run_app_result目录中）
        """
        base_path, _ = os.path.split(sys.argv[0])
        base_path = os.path.join(base_path, "RunResult", "run_app_result")
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        file_path = os.path.join(base_path, file_name)
        if os.path.exists(file_path):
            new_file_name = os.path.join(base_path, time.strftime(
                "%Y-%m-%d_%H-%M-%S", time.localtime(time.time())) + "_{0}".format(file_name))
            shutil.move(file_path, new_file_name)
        return file_path


if __name__ == '__main__':


    data = OrderedDict([("a", "1"), ("b", "2"), ("c", "3"), ("d", "4"), ("e", "5")])
    test = CWriteExcel()
    # file_path = test.write_before("app_run_result.xls")
    # test.write_excel(file_path, data, "test")
    file_path = r"E:\Documents\result_user_rate_2023-04-12.xlsx"
    # data = test.Get_excel_dat(file_path)
    # print(data)
    data = test.Get_excel_data_list(file_path)
    print(data)
    # file_path.encode()
