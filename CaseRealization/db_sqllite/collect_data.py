# -*- coding:utf-8 -*-
from __future__ import unicode_literals
"""
@author:Pengbo
@file:collect_data.py
@className:
@time:2019/8/3 10:53
@function:
数据收集进程
"""

import threading
import time
import psutil
import os
import traceback
from CaseRealization.db_sqllite.Performance_info import PerformanceInfo
from CaseRealization.db_sqllite.Performance_info_ui import CGetSystemPmoniter



class CCollectData(threading.Thread):
    """

    """
    def __init__(self, precess_name, my_sqlite, my_queue, maximum_dir):
        """

        :param precess_name: 进程名称
        :param my_event: event事件  控制线程退出
        :param my_sqlite: 数据库连接对象
        :param my_queue: 线程之间通信的队列
        :param maximum_dir: 各项性能指标的最大值
        """
        super(CCollectData, self).__init__()
        self.process_name = precess_name
        self.my_sqlite = my_sqlite

        self.my_event = threading.Event()
        self.my_event.clear()

        self.my_queue = my_queue
        # 各项值的最大值
        self.maximum_dir = maximum_dir

    def run(self):
        """

        :return:
        """
        if self.process_name.lower().endswith(".exe"):
            table_name, _ = os.path.splitext(self.process_name)
            run_type = 1
        else:
            table_name = self.process_name.replace(" ", "")
            run_type = 2
        # 初始化数据收集
        print(table_name)
        # 表创建
        sql_cmd = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        all_table = self.my_sqlite.Excution_sql(sql_cmd)
        if isinstance(all_table, str):
            print("查表失败")
            # self.my_sqlite.Close_db()
            return
        table_exist = False

        for one in all_table:
            if table_name == one["name"]:
                table_exist = True
                break

        if not table_exist:
            # 表不存在 需要创建
            sql = """CREATE TABLE '{0}'
                       ([process_name] varchar(100),
                        [process_id] int,
                        [cpu_use] float ,
                        [memory] float ,
                        [gpu] float ,
                        [io_read] float ,
                        [io_write] float,
                        [handles] float,
                        [gdi] float,
                        [threads] int,
                        [install_time] float)""".format(table_name)
            result = self.my_sqlite.Excution_sql(sql)
            if isinstance(result, str):
                # self.my_sqlite.Close_db()
                print("创建数据表失败")
                return
        else:
            sql = "delete from '{0}'".format(table_name)
            result = self.my_sqlite.Excution_sql(sql)
            if isinstance(result, str):
                # self.my_sqlite.Close_db()
                print("删除数据表失败")
                return

        self.Run_logic(table_name, run_type)

    def Run_logic(self, table_name, run_type):
        """
        执行数据的收集和插入
        :return:
        """
        if run_type == 1:
            clect_data_clas = PerformanceInfo()
        else:
            clect_data_clas = CGetSystemPmoniter()
            need_control = clect_data_clas.get_need_control()
            process_control = clect_data_clas.get_process_control(need_control["List_of_item"], table_name)
        pid = None
        performance_info_list = []
        process_is_not_exist = False  # 用于判断是否需要向界面发送信号（是否需要向队列中存值） 判断进程是否存在
        performance_is_out_time = time.time()
        performance_is_out_maix = False  # 用于判断是否需要向界面发送信号（是否需要向队列中存值） 判断是否有值超过最大值
        while True:
            time_start = time.time()
            if not pid:
                # 判断进程是否存在 不存在时进入以下逻辑
                pid = self.Get_pid()
                if pid and not process_is_not_exist:
                    temp_static_list = [self.process_name, None, 1]  # 进程已经存在向界面返回正常的 值
                    self.my_queue.put(temp_static_list)
            elif process_is_not_exist:
                temp_static_list = [self.process_name, None, 1]  # 进程已经存在向界面返回正常的 值
                self.my_queue.put(temp_static_list)
                process_is_not_exist = False

            if self.my_event.isSet():
                print("退出收集数据线程:'{0}'".format(table_name))
                # 插入数据
                if performance_info_list.__len__() > 0:
                    self.Insert_data(performance_info_list, table_name)
                    del performance_info_list[:]  # 清除list
                # 提交数据库
                self.my_sqlite.conn.commit()
                # 将event事件设置为false
                self.my_event.clear()
                break

            if run_type == 1:
                # 获取性能数据
                performance_info = clect_data_clas.get_performance_info(pid)
                if performance_info["cpu"] == -1:
                    performance_info["pid"] = -1
                else:
                    performance_info["pid"] = pid

                key_list = ["cpu", "memory", "gpu", "io_read", "io_write",
                            "handles", "GDI", "threads", "time"]
                performance_info["process_name"] = table_name
                for item in key_list:
                    if item not in performance_info.keys():
                        performance_info[item] = -1
            else:
                performance_info = clect_data_clas.get_process_used_pmonitor(process_control)
                key_list = ["cpu", "memory", "gpu", "io_read", "io_write",
                            "handles", "GDI", "threads", "time"]
                performance_info["process_name"] = table_name
                for item in key_list:
                    if item not in performance_info.keys():
                        performance_info[item] = -1

            performance_info_list.append(performance_info)
            # 插入数据
            if performance_info_list.__len__() > 5:
                self.Insert_data(performance_info_list, table_name)
                del performance_info_list[:]  # 清除list

            # 判断进程是否存在
            if performance_info["cpu"] == -1:
                if pid:
                    pid_exist = psutil.pid_exists(pid)
                    if not pid_exist:
                        pid = self.Get_pid()
                else:
                    try:
                        if not process_is_not_exist:
                            temp_static_list = [self.process_name, None, 0]  # 进程不存在 向界面发送信号
                            self.my_queue.put(temp_static_list)
                            process_is_not_exist = True
                        # 如果进程不存在则等待2秒再去获取指定名称的pid，以此降低cpu的使用率
                        time.sleep(2)
                    except:
                        print("返回值给界面出现异常")
            else:
                # elif performance_info["cpu"] > self.maximum_dir["cpu"]:
                if (time.time() - performance_is_out_time) > 5*60 or not performance_is_out_maix:
                    all_performance_is_normal = True
                    try:
                        for key in self.maximum_dir.keys():
                            if performance_info[key] > self.maximum_dir[key]:
                                performance_is_out_time = time.time()
                                if not performance_is_out_maix:
                                    temp_static_list = [self.process_name, key, 2]  # 性能数据超过最大值 向界面发送信号
                                    self.my_queue.put(temp_static_list)
                                all_performance_is_normal = False
                                performance_is_out_maix = True
                                break
                    except:
                        pass
                    if all_performance_is_normal and performance_is_out_maix:
                        temp_static_list = [self.process_name, "cpu", 1]  # 性能数据恢复 向界面发送信号
                        performance_is_out_maix = False
                        self.my_queue.put(temp_static_list)
            time_end = time.time()
            if (time_end - time_start) >= 1:
                continue
            time.sleep(time_end - time_start)

    def Get_pid_buy_name(self, process_name):
        """
        通过进程名获取进程id
        :param process_name:
        :return:
        """
        pid_list = []
        all_pid = psutil.pids()
        for item in all_pid:
            try:
                if psutil.Process(item).name().lower() == process_name.lower():
                    pid_list.append(item)
            except:
                continue
        return pid_list

    def Insert_data(self, performance_info_list, table_name):
        """
        插入数据
        :param performance_info_list:
        :return:
        """
        sql = "insert into '{0}' (process_name, process_id, cpu_use, memory, gpu, io_read, io_write, handles, gdi, " \
              "threads, install_time) values ".format(table_name)
        for one_info in performance_info_list:
            sql += "('{0}', {1}, {2}, {3}, {10},{4}, {5}, {6}, {7}, {8}, {9}),".format(
                self.process_name, one_info["pid"], one_info["cpu"], one_info["memory"], one_info["io_read"],
                one_info["io_write"], one_info["handles"], one_info["GDI"], one_info["threads"], one_info["time"],
                one_info["gpu"])
        sql = sql[:-1]
        self.my_sqlite.Excution_sql(sql)

    def Get_pid(self):
        """
        获取进程的pid
        :param pid:
        :return:
        """
        pid_new = None

        temp_pid = self.Get_pid_buy_name(self.process_name)
        if temp_pid:
            pid_new = temp_pid[0]  # 只取进程列表中的第一个

        return pid_new
