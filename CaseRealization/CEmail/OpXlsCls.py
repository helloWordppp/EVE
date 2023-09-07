# !/usr/bin/env
# -*- coding=utf-8 -*-
'''
Created on 2015��1��29��
@author: xuantianbing
'''
from __future__ import unicode_literals
import xlrd
import xlwt
import logging
import os
import sys
import xlsxwriter
# from Logic.RunType import RunObj

try:
    from collections import OrderedDict as _default_dict
except:
    _default_dict = dict

if getattr(sys, 'frozen', False):
    basepath = os.path.dirname(sys.executable)
elif __file__:
    basepath = os.path.dirname(__file__)
FILE_XLS = 3


class OpXls():
    #操作xls的读与写
    def __init__(self,file_name=None):
        self.__log = logging.getLogger()
        #日志
        self.__wb = xlwt.Workbook(encoding='utf-8')
        #写xls对象
        self.__wb_sheets = []
        self.redstyle = xlwt.XFStyle()
        self.SetSepcityValueType()
        self.filetype = FILE_XLS
        self.file_name=file_name
        #已写了的sheets集合

    def SetSepcityValueType(self):
        refont = xlwt.Font()
        refont.colour_index = 2
        self.redstyle.font = refont

    def Readxls(self, xlsname):
        self._readdata = _default_dict()
        if xlsname != "":
            self.__log.info("Begin read excel file")
            '''用例路径'''
            OCease = xlrd.open_workbook(xlsname)
            '''打开XLs'''
            sh_names = OCease.sheet_names()
            '''循环找到excel文件的sheet内容'''
            for item in sh_names:
                sheet = OCease.sheet_by_name(item)
                self._readdata[item] = self.ReadSheets(sheet)
            self.__log.info("Finish read excel file!")

    def GetReadSheets(self):
        '''
                    返回读取的xls表的sheet名
        '''
        return self._readdata.keys()

    def GetSheetData(self, sheetname):
        '''
                    获取xls的sheet表的数据；
                    如果是sheetname是string，则通过sheetname来查找，并返回对应的表单的数据
                    如果是sheetname是int，则通过索引来查找，并返回对应的表单的数据
        '''
        if isinstance(sheetname, str):
            if sheetname in self.GetReadSheets():
                return self._readdata[sheetname]
            else:
                self.__log.info("sheet not found,check the file!")
                return []
        elif isinstance(sheetname, int):
            if sheetname in range(0, len(self._readdata)):
                sheet_name = list(self._readdata.keys())[sheetname]
                if len(self._readdata[sheet_name]) > 1:
                    return self._readdata[sheet_name][1]
                return self._readdata[sheet_name][0]
            else:
                self.__log.info("index out of the rang,check the file!")
                return []

    def ReadSheets(self, sh_name):
        '''
        @sh_name:根据sheet名获得对应xls文件的sheet表里面的数据
        @return：dict{第一行作为key，每行内容作为value}
        '''
        nrows = sh_name.nrows
        '''获取行数'''
        row = []
        if nrows < 1:
            return [[]]
        for item in sh_name.row_values(0):
            row.append(item)
        '''获取第二行数内容'''
        result = []
        for i in range(1, nrows):
            rowitem = _default_dict()
            for index, item in enumerate(sh_name.row_values(i)):
                if isinstance(item, float):
                    item = int(item)
                item = str(item)
                if "\n" in item:
                    item = item.replace("\n", "<br>")
                rowitem[row[index]] = item
            result.append(rowitem)
        return result

    def _get_not_exist_sheet_name(self):
        icount = 0
        while True:
            sheetname = 'sheet%d'%icount
            if 'sheet%d'%icount not in self.__wb_sheets:
                return sheetname
            else:
                icount += 1

    def WriteXlsByList(self, contents, sheetname=None, rowname=None, \
                       hyperlinks=False, hyperlinks_index=2, \
                       special_value=["No"]):
        '''
        @contents[[]] 二维数组:需要写入的数据
        @sheetname str:表单名
        @rowname   list:第一行内容
        @hyperlinks，hyperlinks_index:是否开启超链接以及超链接的列数
        @special_value：需要特殊显示的数值的集合
        '''
        self.__log.info("begin write data to file sheet name is:%s"%sheetname)
        if contents == [] or not isinstance(contents[0], list):
            self.__log.info('data error!')
            return False
        if sheetname is None or not isinstance(sheetname, basestring):
            sheetname = self._get_not_exist_sheet_name()
        self.__wb_sheets.append(sheetname)
        if rowname is None or not isinstance(rowname, list):
            rowname = []
            map(lambda index: rowname.append('id%d'%index), xrange(len(contents[0])))
        #添加工作表
        self.wbs = self.__wb.add_sheet(sheetname, cell_overwrite_ok=True)
        #写第一行
        for index, item in enumerate(rowname):
            self.wbs.write(0, index, item)
        #写其他行
        for index, item in enumerate(contents):
            for cellindex, cell in enumerate(item):  
                if hyperlinks and isinstance(hyperlinks_index, int) \
                    and cellindex == hyperlinks_index-1 and cell:
                    n = "HYPERLINK"
                    self.wbs.write_merge(index+1, index+1, cellindex, \
                                         cellindex, xlwt.Formula('%s("%s")'%(n, cell)))
                elif cell in special_value:
                    self.wbs.write(index+1, cellindex, cell, self.redstyle)
                else:
                    self.wbs.write(index+1, cellindex, cell)

#     def SaveXls(self, xlsname=None, exetime=None):
    def SaveXls(self, xlsname):
        #保存结果
        self.__wb.save(xlsname)


class WriteXLSX(object):
    """

    """
    def __init__(self, xlsxname):
        '''
        give the xlsx's name
        :param xlsxname:
        '''
        self.__log = logging.getLogger()
        self.__wb_sheets = []
        xlsxpath = xlsxname if os.path.isfile(xlsxname) else os.path.join(basepath, xlsxname)
        if os.path.exists(xlsxpath):
            if os.path.isfile(xlsxpath) and xlsxpath.endswith(".xlsx"):
                self.__wb = xlsxwriter.Workbook(xlsxpath)
            else:
                raise ValueError("need file path or file name end's with .xlsx")
        elif xlsxpath.endswith(".xlsx"):
            self.__wb = xlsxwriter.Workbook(xlsxpath)
        else:
            raise ValueError("need file path or file name end's with .xlsx")
        
    def WriteXlsxByList(self, contents, sheetname=None, rowname=None, \
                       hyperlinks=False, hyperlinks_index=None, \
                       special_value=["No"]):
        '''
        @contents[[]] 二维数组:需要写入的数据
        @sheetname str:表单名
        @rowname   list:第一行内容
        @hyperlinks，hyperlinks_index:是否开启超链接以及超链接的列数
        @special_value：需要特殊显示的数值的集合
        '''
        self.__log.info("begin write data to file sheet name is:%s"%sheetname)
        if contents == [] or not isinstance(contents[0], list):
            self.__log.info('data error!')
            return False
        if sheetname is None or not isinstance(sheetname, basestring):
            sheetname = self._get_not_exist_sheet_name()
        self.__wb_sheets.append(sheetname)
        if rowname is None or not isinstance(rowname, list):
            rowname = []
            map(lambda index: rowname.append('id%d'%index), xrange(len(contents[0])))
        #添加工作表
        self.wbs = self.__wb.add_worksheet(sheetname)
        #写第一行
        for index, item in enumerate(rowname):
            self.wbs.write(0, index, item)
        #写其他行
        if hyperlinks_index is not None:
            hyperlinks_index = tuple(hyperlinks_index) if not  \
                isinstance(hyperlinks_index,(tuple,list)) else hyperlinks_index
        for index, item in enumerate(contents):
            for cellindex, cell in enumerate(item):  
                if hyperlinks_index is not None and hyperlinks and \
                            cellindex+1 in hyperlinks_index and cell:
                    n = "HYPERLINK"
                    self.wbs.write_merge(index+1, index+1, cellindex, \
                                         cellindex, xlwt.Formula('%s("%s")'%(n, cell)))
                elif type(cell) == type(special_value) and cell in special_value:
                    self.wbs.write(index+1, cellindex, cell, self.redstyle)
                else:
                    self.wbs.write(index+1, cellindex, cell)

    def SaveXlsx(self):
        """
        保存excel文件
        :return:
        """
        self.__wb.close()
