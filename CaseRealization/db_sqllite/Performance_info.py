# -*- coding:utf-8 -*-

"""
@author:LuoFeng
@file:Performance_info.py
@className:
@time:2019/8/3 14:26
@function:
收集指定进程的相关性能数据：CPU使用率，内存，I/O读写，句柄 和 GDI对象
"""

import psutil
import time
import win32api
import win32con
import win32process


# class Global_value():
#     last_read = 0
#     last_write = 0

class PerformanceInfo(object):

    def __init__(self, last_read=0, last_write=0):
        self.last_read = last_read
        self.last_write = last_write

    def get_performance_info(self, pid):
        try:
            # 找出本机CPU的逻辑核个数
            cpucount = psutil.cpu_count(logical=True)
            # 传入进程PID，实现监测功能
            process = psutil.Process(int(pid))
            cpupercent = process.cpu_percent(interval=1)
            # 得到进程CPU占用，同资源检测管理器的数据
            cpu = int(cpupercent / cpucount)

            # 进程的内存，单位是KB
            memory = process.memory_info().rss / 1024

            # IO的每秒读取字节,起始时，读取速率是0; 用此刻的读取字节数减去上一秒的读取字节数
            read = process.io_counters().read_bytes
            if self.last_read == 0:
                io_read = 0
            else:
                io_read = read - self.last_read

            self.last_read = read

            # IO的每秒写入字节，起始时，写入速率是0
            write = process.io_counters().write_bytes
            if self.last_write == 0:
                io_write = 0
            else:
                io_write = write - self.last_write

            self.last_write = write

            # 进程的句柄数
            handles = process.num_handles()

            try:
                # 进程的GDI对象
                hprocess = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION |
                                                win32con.PROCESS_VM_READ, False, int(pid))
                GDI = win32process.GetGuiResources(hprocess, win32con.GR_GDIOBJECTS)
            except:
                GDI = 0

            # 线程数
            threads = process.num_threads()

            # 收集数据
            dic = {"cpu": cpu, "memory": memory, "io_read": io_read,
                   "io_write": io_write, "handles": handles, "GDI": GDI,
                   "threads": threads, "time": time.time()}

        except:
            # 可能进程出现异常
            self.last_read = 0
            self.last_write = 0
            dic = {"cpu": -1, "memory": -1, "io_read": -1,
                   "io_write": -1, "handles": -1, "GDI": -1,
                   "threads": -1, "time": time.time()}

        return dic

