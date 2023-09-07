# -*- coding:utf-8 -*-

"""
@author:Pengbo
@file:get_system_info.py
@className:
@time:2019/5/29 9:16
@function:获取系统信息，获取硬件信息

"""
"""
    python中，platform模块给我们提供了很多方法去获取操作系统的信息
    如：
        import platform
        platform.platform()   #获取操作系统名称及版本号，'Windows-7-6.1.7601-SP1'
        platform.version()    #获取操作系统版本号，'6.1.7601'
        platform.architecture()   #获取操作系统的位数，('32bit', 'WindowsPE')
        platform.machine()    #计算机类型，'x86'
        platform.node()       #计算机的网络名称，'hongjie-PC'
        platform.processor()  #计算机处理器信息，'x86 Family 16 Model 6 Stepping 3, AuthenticAMD'
        platform.uname()      #包含上面所有的信息汇总，uname_result(system='Windows', node='hongjie-PC',
                               release='7', version='6.1.7601', machine='x86', processor='x86 Family
                               16 Model 6 Stepping 3, AuthenticAMD')

        还可以获得计算机中python的一些信息：
        import platform
        platform.python_build()
        platform.python_compiler()
        platform.python_branch()
        platform.python_implementation()
        platform.python_revision()
        platform.python_version()
        platform.python_version_tuple()
"""

import platform
import os
import sys
import psutil
import wmi
import pythoncom
import logging
import socket
from collections import OrderedDict


class CGet_system_info:
    """"""
    def __init__(self):
        self.system_info = platform.uname()

    def Get_pc_name(self):
        """获取计算机名"""
        return self.system_info.node

    def Get_pc_ip(self):
        """

        :return:
        """
        # 获取本机ip
        myaddr = socket.gethostbyname(socket.gethostname())
        return myaddr

    def Get_system_info(self):
        """获取完整的系统信息"""
        return platform.platform()

    def Get_system_type(self):
        """获取系统版类型  windows还是mac"""
        return self.system_info.system

    def Get_system_release(self):
        """获取系统版本 7 或者 8 8.1 10"""
        return self.system_info.release

    def Get_system_version(self):
        """获取系统版本 好  eg:6.1.7601"""
        return self.system_info.version

    def Get_system_bite(self):
        """获取操作系统位数"""
        # get type of machine.
        if os.name == 'nt' and sys.version_info[:2] < (2, 7):
            machine = os.environ.get("PROCESSOR_ARCHITEW6432", os.environ.get('PROCESSOR_ARCHITECTURE', ''))
        else:
            machine = platform.machine()

        """Return bitness ofoperating system, or None if unknown."""
        machine2bits = {'AMD64': 64, 'x86_64': 64, 'i386': 32, 'x86': 32}
        return machine2bits.get(machine, None)


class CGet_pc_info:
    """获取计算机硬件信息"""
    def __init__(self):
        pythoncom.CoInitialize()  # 使用了win32com 在多线程时就需要

    def Free_source(self):
        """释放资源"""
        pythoncom.CoUninitialize()

    def Get_cpu_core(self):
        """获取cpu核心数"""
        return psutil.cpu_count(logical=False)

    def Get_cpu_thread(self):
        """获取cpu线程数"""
        return psutil.cpu_count()

    def Get_cpu_type(self):
        """获取cpu的类型 eg：Intel(R) Core(TM) i7 CPU         920  @ 2.67GHz"""
        if not self.my_wmi:
            self.my_wmi = wmi.WMI()
        cpu_type = ""
        for cpu in self.my_wmi.Win32_Processor():
            cpu_type = cpu.Name
        return cpu_type

    def Get_disk_info(self):
        """获取硬盘信息"""
        if not self.my_wmi:
            self.my_wmi = wmi.WMI()
        disks = []
        for disk in self.my_wmi.Win32_DiskDrive():
            # print disk.__dict__
            tmpmsg = OrderedDict()
            tmpmsg['SerialNumber'] = disk.SerialNumber.strip()
            tmpmsg['DeviceID'] = disk.DeviceID
            tmpmsg['Caption'] = disk.Caption
            tmpmsg['Size'] = disk.Size
            tmpmsg['UUID'] = disk.qualifiers['UUID'][1:-1]
            disks.append(tmpmsg)
        for d in disks:
            print(d)

        return disks

    def Get_memory_info(self):
        """获取系统总的安装内存"""
        memory = psutil.virtual_memory()
        print(memory.total)
        return memory.total


def Get_max_free_partition():
    """获取最大剩余空间"""
    tmplist = []
    pythoncom.CoInitialize()
    mywmi = wmi.WMI()
    for physical_disk in mywmi.Win32_DiskDrive():
        for partition in physical_disk.associators("Win32_DiskDriveToDiskPartition"):
            for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                try:
                    tmpdict = OrderedDict()
                    tmpdict["Caption"] = logical_disk.caption
                    tmpdict["FreeSpace"] = float(logical_disk.FreeSpace) / 1024 / 1024 / 1024
                    tmplist.append(tmpdict)
                except Exception as e:
                    print(logging.exception(e))
    pythoncom.CoUninitialize()
    ret = sorted(tmplist, key=lambda tmp: tmp["FreeSpace"], reverse=True)
    if not ret:
        dir_path, _ = os.path.split(sys.argv[0])
        print("Get_max_free_partition failed:", dir_path[:3])
        return dir_path[:3]

    print("the big partition is:", ret[0]["Caption"]+"\\")
    return ret[0]["Caption"]+"\\"


def Get_run_process_info():
    """获取所有正在运行的程序的信息（pid，名称, 用户, 位置, 创建时间）"""
    pidList = psutil.pids()
    result_all = []
    for pid in pidList:
        try:
            attrs_list = ['pid', 'name', 'username', 'exe', 'create_time', 'ppid', 'cmdline', 'threads', 'memory_maps']
            pid_dictionary = psutil.Process(pid).as_dict(attrs=attrs_list)
            result_all.append(pid_dictionary)
        except:
            pass
    print(result_all)
    return result_all


if __name__ == '__main__':
    Get_run_process_info()
    # test = CGet_pc_info()
    # test.Get_memory_info()
