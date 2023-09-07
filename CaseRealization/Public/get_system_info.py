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
import traceback
import ctypes
from ctypes import c_char_p
import string
from collections import OrderedDict


class CGet_system_info:
    """
    获取系统信息
    """
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
        """获取操作系统位数, 返回32或者64"""
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
    """
    获取所有正在运行的程序的信息（pid，名称, 用户, 位置, 创建时间）
    psutil.Process(2029)
    print(os.getpid())
    ss = psutil.Process(11532)
    print(dir(ss))
    print(ss.ppid())
    print(ss.parent())
    print(ss.cmdline())
    print(ss.cwd())
    print(ss.io_counters())
    print(ss.ionice())
    print(ss.exe())
    print(ss.environ())
    print(ss.cwd())
    print(ss.memory_full_info())
    print(ss.memory_info())
    print(ss.memory_info_ex())
    print(ss.memory_maps())
    print(ss.memory_maps()[0].path)
    print(ss.memory_maps()[0].rss)
    print(ss.threads())
    :return:
    """
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


def Get_child_process(ppid):
    """
    获取某一进程的子进程
    :param ppid: 父进程pid
    :return: 子进程列表
    """
    all_pids = Get_run_process_info()
    child_list = []
    for item in all_pids:
        if item["ppid"] == ppid:
            child_list.append(item)
    return child_list


def Get_pid_buy_name(process_name):
    """
    通过进程名获取进程id
    :param process_name:进程名 需要带上后缀如PCTrans.exe
    :return:
    """
    pid_list = []
    for item in psutil.pids():
        try:
            if psutil.Process(item).name().lower() == process_name.lower():
                pid_list.append(item)
        except:
            continue
    return pid_list


def Get_all_runExe_LocalPath():
    """
    获取所有正在运行的程序的信息（pid，name, username, path, 创建时间）
    :return: 所有正在运行的程序的信息
    """
    try:
        pid_list = psutil.pids()
    except:
        pid_list = []
    result_all = []

    for pid in pid_list:
        try:
            result_one = OrderedDict([("pid", 0), ("name", ""), ("username", ""), ("exe_path", ""),
                                      ("creat_time", ""), ("cmdline", ""), ("ppid", 0)])
            process_info = psutil.Process(pid).as_dict(attrs=['pid', 'name', 'username', 'exe', 'create_time',
                                                              "cmdline", "ppid"])
            result_one["pid"] = process_info["pid"]
            result_one["name"] = process_info["name"]
            result_one["username"] = process_info["username"]
            result_one["exe_path"] = process_info["exe"]
            result_one["create_time"] = process_info["create_time"]
            result_one["cmdline"] = process_info["cmdline"]
            result_one["ppid"] = process_info["ppid"]
            # result_one["parent"] = process_info["parent"]
        except:
            continue
        result_all.append(result_one)
    return result_all


def Get_child_info(pid):
    """
    获取某一进程的所有子孩子
    :param all_process_info:
    :return:
    """
    all_process_info = Get_all_runExe_LocalPath()
    temp_pid = []
    for item in all_process_info:
        if pid == item["ppid"]:
            temp_pid.append(item)
            # child_list = Get_all_child_info(all_process_info, item["pid"])

    return temp_pid


def Get_process_info_by_name(process_name):
    """
    获取指定进程的信息
    :param process_name: 进程名称，带exe忽略大小写
    :return: 进程信息列表
    """
    all_process_info = Get_all_runExe_LocalPath()
    process_info = []
    for item in all_process_info:
        if item["name"] and item["name"].lower() == process_name.lower():
            process_info.append(item)
    return process_info


def Get_process_info_by_pid(process_pid):
    """
    获取指定进程的信息
    :param process_name: 进程pid
    :return: 进程信息
    """
    all_process_info = Get_all_runExe_LocalPath()
    process_info = None
    for item in all_process_info:
        if item["pid"] and item["pid"] == process_pid:
            process_info = item
    return process_info


def get_disk_list_exists():
    """
    获取本机所有的盘符
    :return:
    """
    disk_list = []
    for c in string.ascii_uppercase:
        disk = c + ':'
        if os.path.isdir(disk):
            disk_list.append(disk)
    print(disk_list)
    return disk_list


def get_disk_list_no_exists():
    """
    获取本机不存在的盘符
    :return:
    """
    disk_list = []
    for c in string.ascii_uppercase:
        disk = c + ':'
        if not os.path.isdir(disk):
            disk_list.append(disk)
    print(disk_list)
    return disk_list


def test_network_connect(net_list=None):
    """
    测试1.110 和0.182 是否可以连接
    :param net_list: list
    :return:
    """
    if not net_list:
        net_list = [r"\\192.168.1.110\产品发布", r"\\192.168.0.182\测试资源"]
    if not isinstance(net_list, list):
        raise Exception("net_list error.")
    need_connect = False
    for item in net_list:
        if not os.path.exists(item):
            need_connect = True
            break
    if need_connect:
        return True
    return False


def set_network_connect():
    """
    设置网络链接
    :return:
    """
    if not test_network_connect():
        return True
    net_work1 = r"\\192.168.1.110"
    net_work2 = r"\\192.168.0.182"
    user1 = "easeus"
    user2 = "csb"
    pwd1 = "easeus"
    pwd2 = "easeus"

    cmd1 = 'net use {0} {1} /user:{2}'.format(net_work1, pwd1, user1)
    cmd2 = 'net use {0} {1} /user:{2}'.format(net_work2, pwd2, user2)
    try:
        os.popen(cmd1)
        os.popen(cmd2)
    except:
        print(traceback.format_exc())
        return False
    return True


def set_network_connect_in():
    """
    设置网络链接内网0.242
    :return:
    """
    if not test_network_connect([r"\\192.168.0.242\产品发布"]):
        return True
    net_work1 = r"\\192.168.0.242"
    user1 = "csb"
    pwd1 = "easeus"
    cmd1 = 'net use {0} {1} /user:{2}'.format(net_work1, pwd1, user1)
    try:
        os.popen(cmd1)
    except:
        print(traceback.format_exc())
        return False
    return True


def set_network_connect_in172():
    """
    设置网络链接内网0.242
    :return:
    """
    if not test_network_connect([r"\\172.17.188.242\产品发布"]):
        return True
    net_work1 = r"\\172.17.188.242"
    user1 = "csb"
    pwd1 = "easeus"
    cmd1 = 'net use {0} {1} /user:{2}'.format(net_work1, pwd1, user1)
    try:
        os.popen(cmd1)
    except:
        print(traceback.format_exc())
        return False
    return True



def SetThreadExecutionState():
    """
    调用windos api 设置电脑屏幕不息屏，不休眠
    :return:
    """
    """
    ES_AWAYMODE_REQUIRED
    0x00000040
    启用离开模式。必须使用ES_CONTINUOUS指定此值。
    离开模式只能由必须在台式机上执行关键后台处理的媒体记录和媒体分发应用程序使用，而计算机似乎正在休眠。请参阅备注。

    ES_CONTINUOUS
    0x80000000
    通知系统所设置的状态应保持有效，直到使用ES_CONTINUOUS的下一个调用和其他状态标志之一被清除为止。
    ES_DISPLAY_REQUIRED
    0x00000002
    通过重置显示器空闲计时器来强制显示器开启。
    ES_SYSTEM_REQUIRED
    0x00000001
    通过重置系统空闲计时器来强制系统进入工作状态。
    ES_USER_PRESENT
    0x00000004
    不支持该值。如果将ES_USER_PRESENT与其他esFlags值组合，则调用将失败，并且不会设置任何指定状态。
    """
    # https://docs.microsoft.com/zh-cn/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate?redirectedfrom=MSDN
    ES_CONTINUOUS = 0x80000000
    ES_DISPLAY_REQUIRED = 0x00000002
    ES_SYSTEM_REQUIRED = 0x00000001
    try:
        kernel32 = ctypes.WinDLL('kernel32.dll')
        result = kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED)
    except:
        print("-----SetThreadExecutionState----error -----")
        print(traceback.format_exc())


def MessageBoxA(lpText=None, lpCaption=None, hWnd=None, uType=0x00000000):
    """
    中文显示会乱码
    这离只是显示一个简单的只有一个ok按钮的弹窗，详细的设置 可以参看微软官网
    :param hWnd: 父窗口句柄
    :param lpText:窗口内容
    :param lpCaption:窗口标题
    :param uType:窗口类型
                    MB_ABORTRETRYIGNORE             0x00000002   该消息框包含三个按钮：中止，重试和忽略。
                    MB_CANCELTRYCONTINUE            0x00000006   该消息框包含三个按钮：取消，重试，继续。使用此消息框类型代替MB_ABORTRETRYIGNORE。
                    MB_HELP                         0x00004000   将帮助按钮添加到消息框中。当用户单击“ 帮助”按钮或按F1时，系统将WM_HELP消息发送给所有者。
                    MB_OK                           0x00000000   该消息框包含一个按钮：OK。这是默认值。
                    MB_OKCANCEL                     0x00000001   该消息框包含两个按钮：“ 确定”和“ 取消”。
                    MB_RETRYCANCEL                  0x00000005   该消息框包含两个按钮：重试和取消。
                    MB_YESNO                        0x00000004   该消息框包含两个按钮：是和否。
                    MB_YESNOCANCEL                  0x00000003   该消息框包含三个按钮：是，否和取消。
    :return:
    """
    # url:https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messageboxa
    if hWnd and not isinstance(hWnd, int):
        print("hWnd type error.")
        return False
    # if lpText and not isinstance(lpText, str):
    #     print("lpText type error.")
    #     return False
    if lpCaption and not isinstance(lpCaption, str):
        print("lpCaption type error.")
        return False
    try:
        user_choose = ctypes.windll.user32.MessageBoxA(hWnd, c_char_p(str(lpText).encode("utf-8")),
                                                       c_char_p(str(lpCaption).encode("utf-8")), uType)
        print(user_choose)
    except:
        print(traceback.format_exc())
        return False
    return True





if __name__ == '__main__':
    print(os.getpid())
    import time
    all_child = Get_child_info(6968)
    for item in all_child:
        print(item["pid"])
        # time.sleep(10)
    print(all_child)
