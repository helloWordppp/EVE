# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:Run.py
@className:
@time:2019/7/25 16:44
@function:

"""
import os
import traceback
import sys
from CaseRealization.CEmail.Mail import MyMail
from CaseRealization.CEmail.Report import ClsReport
from CaseRealization.Public.read_ini import ConfigRead


class CSendEmail:
    def __init__(self):
        self.receive = ["314476053@qq.com"]
        self.sender_name = "314476053@qq.com"
        self.sender_pwd = "nnifisldxtoncbch"
        self.product = ''
        self.version = ""
        self.comp = []
        self.smtp_address = ""
        self.context = ""
        self.Init_info()

    def Init_info(self):
        """
        从配置文件  Email.ini中 获取基本信息
        :return:
        """
        dir_path, _ = os.path.split(sys.argv[0])
        email_config = os.path.join(dir_path, "Config", "Email.ini")
        if not os.path.exists(email_config):
            raise Exception("配置文件不存在:", email_config)
        my_ini = ConfigRead()
        my_ini.GetData(email_config)

        self.sender_name = my_ini.get("Email", "sender_name")
        self.smtp_address = my_ini.get("Email", "smtp_address")
        self.sender_pwd = my_ini.get("Email", "sender_pwd")
        self.product = my_ini.get("Product", "name")
        self.version = my_ini.get("Product", "version")
        receive_str = my_ini.get("Email", "receive")
        self.receive = [self.sender_name]
        for item in receive_str.split(";"):
            if item and item != "" and item not in self.receive:
                self.receive.append(item)
        self.context = ""

    def Send(self, excel_path, begin_time, end_time, protity, comp=None):
        """
        发送邮件接口
        :param excel_path:结果excel地址
        :param begin_time:开始时间  格式 %Y-%m-%d %H:%M:%S
        :param end_time:结束时间 %Y-%m-%d %H:%M:%S
        :param protity:用例级别
        :param comp:附件  注意是list
        :return:
        """
        mycls = ClsReport()

        mycls.run_time = begin_time
        mycls.begin_time = begin_time
        mycls.end_time = end_time
        mycls.protity = protity

        mycls.version = self.version
        mycls.product = self.product
        mycls.easrst_time = mycls.Get_easrst_time()

        if not self.comp and not comp:
            self.comp = [excel_path]
        if comp:
            for item in comp:
                self.comp.append(item)
        send_times = 1
        while send_times < 10:
            try:
                mymail = MyMail(excel_path, mycls, comp=self.comp, receiver_list=self.receive,
                                sender=self.sender_name, password=self.sender_pwd, smtp_address=self.smtp_address,
                                product=self.product)
                mymail.context = self.context
                mymail.ExecuteMails()
                break
            except:
                send_times = send_times + 1
                print("send email failed, retry:{0}".format(send_times))
                print(traceback.format_exc())
