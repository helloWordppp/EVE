# -*- coding:utf-8 -*-

from __future__ import unicode_literals
"""
@author:Pengbo
@file:thread_management.py
@className:
@time:2019/8/3 13:30
@function:
线程管理
"""

import os
import sys
import traceback
import time
from collections import OrderedDict
from multiprocessing import Queue
from CaseRealization.db_sqllite.collect_data import CCollectData
from CaseRealization.db_sqllite.DBcrud import CSqllite
from CaseRealization.db_sqllite.logging_print import MyLogPrint
from CaseRealization.db_sqllite.notification_thread import CNotification


class CThreadManage(object):
    """

    """
    def __init__(self):
        """"""
        # 程序执行路劲
        self.dir_path, _ = os.path.split(sys.argv[0])
        # 删除原有的数据库文件
        # self.Clear_db_file()

        # 用于存放线程
        self.thread_dic = OrderedDict()
        # 数据库操作对象
        self.my_sqlite = CSqllite()

        self.my_queue = Queue()

        # 日志对象
        log_path = os.path.join(self.dir_path, "Log")
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_file_path = os.path.join(log_path, "thread_manage.log")
        self.my_log = MyLogPrint(log_file_path)

        self.my_notification = CNotification()
        self.Start_notification()

    def Start_notification(self):
        """
        消息队列获取
        :return:
        """
        self.my_notification.q = self.my_queue
        self.my_notification.start()

    def Start_thread(self, process_name, maximum_dir):
        """
        启动一个线程，用于记录某一进程的性能数据
        :param process_name:进程名称 带后缀的 如PCTrans.exe  字符串类型
        :param process_name:各项性能监控指标的最大值 类型字典
        :return:
        """
        one_thread = CCollectData(process_name, self.my_sqlite, self.my_queue, maximum_dir)
        try:
            one_thread.start()
        except:
            error = traceback.format_exc()
            self.my_log.print_info(error)
            return False
        self.thread_dic[process_name] = one_thread
        return True

    def Stop_thread(self, process_name):
        """
        停止一个数据采集线程
        :param process_name:
        :return:
        """
        if not process_name in list(self.thread_dic.keys()):
            self.my_log.print_info("没有改进程")
            return False
        one_thread = self.thread_dic[process_name]
        one_thread.my_event.set()
        return True

    def Uninit(self):
        """
            反初始化，释放资源
        """
        print("退出程序")
        for thread in self.thread_dic.keys():
            self.thread_dic[thread].my_event.set()
            self.thread_dic[thread].join()
        self.my_sqlite.Close_db()

    def Clear_db_file(self):
        """
        删除原有的db文件
        :return:
        """
        db_path = os.path.join(self.dir_path, "DB_data")
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        db_file_path = os.path.join(db_path, "performance_data.db")
        if os.path.exists(db_file_path):
            try:
                os.remove(db_file_path)
            except:
                print(traceback.format_exc())
                return False
        return True

    def Update_maximum_dir(self, process_name, maximum_dir):
        """
        改变阀值
        :param process_name: 进程名不带.exe
        :param maximum_dir: 阀值dir
        :return:
        """
        if not process_name in list(self.thread_dic.keys()):
            self.my_log.print_info("没有改进程")
            return False
        try:
            one_thread = self.thread_dic[process_name]
            one_thread.maximum_dir = maximum_dir
        except:
            return False
        return True


if __name__ == '__main__':
    test = CThreadManage()
    test.Start_thread("RecExperts", {})

    time.sleep(50)
    test.Stop_thread("RecExperts")
