#!/usr/bin/env
# -*- coding=utf-8 -*-

'''
Created on 2014年10月28日
@author: Xuantianbing
'''
import os,time
import socket
import platform
import sys
from CaseRealization.Public.get_system_info import CGet_system_info


def SetReportBody(content_table, td_style, td_image_style, td_fail_style, content_list):
    '''
           根据各个用例的执行结果放入到email的表格中，
           包括了：用例名，执行情况（pass，fail），截图保存位置
    '''
    result = content_table
    if not content_list:
        return result

    if content_list:
        for index, (key, _) in enumerate(content_list[0].items()):
            if 0 == index:
                result += "<tr>" + td_style.format(key)
            elif len(content_list[0].items()) - 1 == index:
                result += td_style.format(key) + "</tr>"
            else:
                result += td_style.format(key)
        for _, item in enumerate(content_list):
            for index, (_, value) in enumerate(item.items()):
                try:
                    value = value if isinstance(value, str) else str(value)
                    if 0 == index:
                        result += "<tr>" + td_style.format(value)
                    elif len(item.items()) - 1 == index:
                        result += td_style.format(value) + "</tr>"
                    else:
                        if value.lower() == 'fail':
                            result += td_fail_style.format(value)
                        else:
                            result += td_style.format(value)
                except:
                    continue
    
        return result
    else:
        return ""


def machine():
    """Return type of machine."""
    if os.name == 'nt' and sys.version_info[:2] < (2,7):
        return os.environ.get("PROCESSOR_ARCHITEW6432",
               os.environ.get('PROCESSOR_ARCHITECTURE', ''))
    else:
        return platform.machine()


def os_bits():
    """
    获取计算机的位数
    :return:
    """
    machine = machine()
    machine2bits = {'AMD64': 64, 'x86_64': 64, 'i386': 32, 'x86': 32}
    return machine2bits.get(machine, None)


def get_machine():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    os_system =  "{0} {1}位".format(platform.platform(), os_bits())
    return "执行机器名:{0}<br>执行机器IP地址:{1}<br>执行机器操作系统:{2}".format(hostname.decode("gbk"), ip, os_system)


class ClsReport:
    def __init__(self):
        self.product = ""
        self.version = ""
        self.run_time = ""
        self.begin_time = ""
        self.end_time = ""
        self.easrst_time = ""
        self.auto_Machine = self.GetPCMachin()
        self.protity = ""
        self.case_total_count = 0
        self.case_fail_count = 0
        self.present = 0

    def Get_easrst_time(self):
        if self.begin_time is None:
            return ""
        bt = time.mktime(time.strptime(str(self.begin_time), "%Y-%m-%d %H:%M:%S"))
        et = time.mktime(time.strptime(str(self.end_time), "%Y-%m-%d %H:%M:%S"))
        easrst = et - bt
        hour = int(easrst/3600)
        minute = int((easrst % 3600)/60)
        sec = int((easrst % 3600) % 60)
        return "{0}:{1}:{2}".format(hour, minute, sec)

    def GetPCMachin(self):
        """
        获取本机计算机信息
        :return:
        """
        my_test = CGet_system_info()
        PcName = my_test.Get_pc_name()
        PcIP = my_test.Get_pc_ip()
        PcSys = my_test.Get_system_type() + my_test.Get_system_release() + "(" + my_test.Get_system_version() \
                + ")" + "_X" + str(my_test.Get_system_bite())
        return "执行机器名:{0}<br>执行机器IP地址:{1}<br>执行机器操作系统:{2}".format(PcName, PcIP, PcSys)

    def SetReportHead(self, content_table, context,  td_style, td_image_style, td_style_fail, clsreport, clxls):
        '''
              通过修改报告的Demo的样式来
               修改实际的邮件报告的头部,
        case_list:获得用例数，失败数，百分比，占位"" 的list
        '''
        context = context.format(self.product, self.version,
                                     self.run_time, 
                                     str(self.begin_time)[0:19], 
                                     str(self.end_time)[0:19], 
                                     self.easrst_time, 
                                     self.auto_Machine,
                                     self.protity)
        for index, item in enumerate(clxls.GetReadSheets()):
            if clxls.GetSheetData(index):
                context += "SheetName:{0}<br>".format(item)
                context += SetReportBody(content_table, td_style, td_image_style, td_style_fail, clxls.GetSheetData(item))
                context += '</TABLE>'
        
        return context

    def CreateReport(self, content_table, myclsreport, context, func_type, td_style, td_image_style, td_style_fail, clxls):
        '''
                根据自动化执行的结果来创建邮件报告,需要计算总的用例数和未通过的用例数
         result_list：自动化执行结果
        '''
        #失败的用例数统计
        print("Begin create auto report!")
 
        func_type_str = ""
        for item in clxls.GetReadSheets():
            
            fail_count = 0
            total_count = 0
            for data in clxls.GetSheetData(item):
                #print data, type(data)
                if data:
                    try:
                        if data['Result'].lower().strip() != 'pass':
                            fail_count += 1
                    except:
                        pass
                    try:
                        if data['result'].lower().strip() != 'pass':
                            fail_count += 1
                    except:
                        pass
                    total_count += 1

            if total_count:
                persent = 100 - float(fail_count) / float(total_count ) * 100
            else:
                persent = 0

            func_type_str += func_type.format(item, str(total_count), str(fail_count), 
                                              str(round(persent, 2)))        
        context += func_type_str
        context = self.SetReportHead(content_table, context, td_style, td_image_style, td_style_fail, myclsreport, clxls)
        print("Create auto report finish!")
        return context
