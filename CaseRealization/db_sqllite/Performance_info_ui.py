# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:Performance_info_ui.py
@className:
@Create Data:2023/5/16 11:18 14:08
@Description:

"""
import time
import os
import sys
import psutil
import uiautomation
import traceback
# import ctypes
import locale
from collections import OrderedDict
from multiprocessing import Process, Event
from multiprocessing import Queue
from CaseRealization.db_sqllite.DBcrud import CSqllite
from CaseRealization.Public.logging_print import MyLogPrint


class CGetSystemPmoniter():
    def __init__(self, my_log=None):
        dir_path, _ = os.path.split(sys.argv[0])
        if my_log is None:
            log_path = os.path.join(dir_path, "Log")
            if not os.path.exists(log_path):
                os.makedirs(log_path)
            log_path_full = os.path.join(log_path, "CGetSystemPmoniter.log")
            self.my_log = MyLogPrint(log_path_full)
        else:
            self.my_log = my_log
        self.language = locale.getdefaultlocale()[0].lower().lower()
        if "cn" in self.language:
            self.window_name = "任务管理器"
            self.window_class_name = "TaskManagerWindow"
        else:
            self.window_name = "Task Manager"
            self.window_class_name = "TaskManagerWindow"
        self.main_product = self.Get_main_handle()
        if not self.main_product:
            self.my_log.print_info("主程序窗口未找到，无法进行后续流程")
            self.main_product = None
            raise Exception("任务管理器窗口未找到")
        else:
            # self.main_product.SetTopmost(True)
            pass

    def Get_main_handle(self, time_out=60):
        """
        获取主程序窗口的Control对象
        :return:
        """
        time_begin = time.time()
        main_product = None
        desktop = uiautomation.GetRootControl()
        # all_child =
        while True:
            time.sleep(1)
            # uiautomation.WindowControl(searchDepth=1, ClassName="Qt5QWindow", Name=r"EaseUS Todo PCTrans")
            for one_child in desktop.GetChildren():
                try:
                    # print(one_child.Name, one_child.ClassName)
                    if one_child.Name == self.window_name and self.window_class_name in one_child.ClassName:
                        main_product = one_child
                        break
                    if one_child.ClassName == "#32770" and one_child.Name == "tip":
                        try:
                            one_child.GetChildren()[0].Click()
                        except:
                            pass
                except:
                    pass
            if main_product and main_product.Exists() and main_product.IsEnabled:
                break
            if (time.time() - time_begin) > time_out:
                break
        return main_product

    def Get_all_child(self, main_ele, all_child_list=[]):
        """
        获取某一控件的所有子控件
        :param main_ele:
        :return:
        """
        all_child = main_ele.GetChildren()
        for item in all_child:
            all_child_list.append(item)
            all_child_list = self.Get_all_child(item, all_child_list)
        return all_child_list

    def get_need_control(self):
        """
        获取所需要的进程控件
        :return:
        """
        all_control = []

        all_control = self.Get_all_child(self.main_product, all_control)

        MenuItemsScrollViewer = None
        ColumnHeader = None
        List_of_item = None

        if "cn" in self.language:
            MenuItemsScrollViewerName = ""
            ColumnHeaderName = "列标题"
            List_of_itemName = "项目列表"
        else:
            MenuItemsScrollViewerName = "MenuItemsScrollViewer"
            ColumnHeaderName = "Column header"
            List_of_itemName = "List of items"

        for item in all_control:
            if item.Name == MenuItemsScrollViewerName and item.ClassName == "ScrollViewer" and item.ControlTypeName == "PaneControl":  # 左侧功能table列表
                MenuItemsScrollViewer = item
                continue
            if item.Name == ColumnHeaderName and item.ClassName == "TmColumnHeader" and item.ControlTypeName == "HeaderControl":  # 顶部系统总的占用
                ColumnHeader = item
                continue
            if item.Name == List_of_itemName and item.ClassName == "TmScrollViewer" and item.ControlTypeName == "DataGridControl":  # 顶部系统总的占用
                List_of_item = item
                continue

            if MenuItemsScrollViewer and ColumnHeader and List_of_item:
                break

        return OrderedDict([("MenuItemsScrollViewer", MenuItemsScrollViewer), ("ColumnHeader", ColumnHeader),
                            ("List_of_item", List_of_item)])

    def get_process_control(self, List_of_item, process_show_name="RecExperts"):
        """
        寻找指定应用的control
        :param List_of_item:
        :param process_show_name:
        :return:
        """
        Background_processes = None
        Apps = None
        all_child = List_of_item.GetChildren()
        for item in all_child:
            # print("-----0", item.Name)
            if item.Name == "Apps" or item.Name == "应用":
                Apps = item
            elif "Background processes" in item.Name or "后台进程" in item.Name:
                Background_processes = item
            elif process_show_name.lower() in item.Name.lower():
                return item
            else:
                try:
                    temp_list = item.GetChildren()
                    if len(temp_list) < 1:
                        continue
                    for child_child in [1].GetChildren():
                        print("item.GetChildren-----1-", child_child.Name)
                        if process_show_name.lower() in child_child.Name.lower():
                            return item
                except:
                    print(traceback.format_exc())
        if Background_processes is None or Apps is None:
            return None

        process_item = None

        for item in Apps.GetChildren():
            print("-----Apps name--", item.Name)
            if process_show_name.lower() in item.Name.lower():
                process_item = item
                return process_item
            else:
                try:
                    temp_list = item.GetChildren()
                    if len(temp_list) < 1:
                        continue
                    for child_child in item.GetChildren()[1].GetChildren():
                        print("item.GetChildren-----2-", child_child.Name)
                        if process_show_name.lower() in child_child.Name.lower():
                            return item
                except:
                    print(traceback.format_exc())

        for item in Background_processes.GetChildren():
            print("-----Background_processes name:--", item.Name)
            if process_show_name.lower() in item.Name.lower():
                process_item = item
                return process_item

        return process_item

    def get_process_used_pmonitor(self, process_item):
        """
        获取进程占用的资源信息
        :param process_item:
        :return:
        """
        try:
            process_all = process_item.GetChildren()[0]
            all_control = process_all.GetChildren()
            process_info = OrderedDict()
            # key_list = ["cpu", "memory", "gpu", "io_read", "io_write",
            #                             "handles", "GDI", "threads", "time"]
            for item in all_control:
                if item.ControlTypeName != "EditControl":
                    continue
                item_name = item.Name
                item_value = item.GetValuePattern().Value
                item_value = item_value.replace(",", "")
                print(item_name, item_value)
                if item_name == "内存" or item_name == "Memory":
                    item_name = "memory"
                    item_value = float(item_value.split(" ")[0])
                elif item_name == "磁盘" or item_name == "Disk":
                    item_name = "io_read"
                    item_value = float(item_value.split(" ")[0])
                elif item_name == "网络" or item_name == "Network":
                    item_name = "Network"
                if isinstance(item_value, str) and "%" in item_value:
                    item_value = float(item_value.replace("%", ""))

                process_info[item_name.lower()] = item_value
            process_info["time"] = time.time()
        except:
            print(traceback.format_exc())
            return process_info
        # print(process_info)
        return process_info


class CPmoniterProcess(Process):
    """
    数据采集进程
    """
    def __init__(self, exit_event, process_show_name="EaseUS VoiceWave", process_name=""):
        super(CPmoniterProcess, self).__init__()
        # db文件保存位置
        time_now = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))
        self.dir_path, _ = os.path.split(sys.argv[0])
        db_path = os.path.join(self.dir_path, "DB_data")
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        self.db_file_path = os.path.join(db_path, "performance_data_{0}.db".format(time_now))

        self.my_event = exit_event
        self.process_show_name = process_show_name
        # 程序执行路劲
        self.dir_path, _ = os.path.split(sys.argv[0])
        self.maximum_dir = {}
        self.process_name = process_name
        self.my_sqlite = None

        self.my_queue = Queue()

    def run(self):

        # 数据库操作对象
        self.my_sqlite = CSqllite(db_file_path=self.db_file_path)

        table_name = self.process_name
        # 初始化数据收集
        print("db table name", table_name)
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

        self.Run_logic(table_name)

    def Run_logic(self, table_name):
        """
        执行数据的收集和插入
        :return:
        """

        get_info = CGetSystemPmoniter()
        need_control = get_info.get_need_control()
        print("process_show_name:", self.process_show_name)

        pid = None
        performance_info_list = []
        process_is_not_exist = False  # 用于判断是否需要向界面发送信号（是否需要向队列中存值） 判断进程是否存在
        performance_is_out_time = time.time()
        performance_is_out_maix = False  # 用于判断是否需要向界面发送信号（是否需要向队列中存值） 判断是否有值超过最大值
        while True:
            try:
                process_control = get_info.get_process_control(need_control["List_of_item"], self.process_show_name)
                if process_control is None:
                    time.sleep(3)
                    if self.process_show_name == "RecExperts":
                        new_name = "EaseUsMainWindow"
                    elif self.process_show_name == "EaseUsMainWindow":
                        new_name = "RecExperts"
                    process_control = get_info.get_process_control(need_control["List_of_item"], new_name)
                    if process_control is None:
                        raise Exception("没有找到进程")
            except:
                print(traceback.format_exc())
                if self.my_event.is_set():
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
                continue

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

            if self.my_event.is_set():
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
            # print("----", process_control.IsEnabled, dir(process_control))
            performance_info = get_info.get_process_used_pmonitor(process_control)
            performance_info["pid"] = pid
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
                if (time.time() - performance_is_out_time) > 5 * 60 or not performance_is_out_maix:
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
            time.sleep(1-(time_end - time_start))

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
            sql += "('{0}', {1}, {2}, {3}, {10}, {4}, {5}, {6}, {7}, {8}, {9}),".format(
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


def start_performance(process_show_name="RecExperts", process_name="RecExperts.exe"):
    """
    开始进行性能数据采集
    :return:
    """
    try:
        exit_event = Event()
        test = CPmoniterProcess(exit_event, process_show_name=process_show_name, process_name=process_name)

        test.start()
        time.sleep(15)
    except:
        print(traceback.format_exc())
        return ""

    return test.db_file_path, exit_event


def stop_perfaormance(exit_event):
    """
    停止采集性能数据
    :param exit_event:
    :return:
    """

    exit_event.set()


if __name__ == '__main__':
    language = locale.getdefaultlocale()[0]
    print(language)
    for i in range(0, 4):
        exit_event = Event()
        test = CPmoniterProcess(exit_event, process_show_name="RecExperts", process_name="RecExperts.exe")

        test.start()
        time.sleep(15)
        time.sleep(60)
        exit_event.set()

        print("----------------2", test.db_file_path)