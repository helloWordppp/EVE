# -*- coding:utf-8 -*-

"""
@author:Pengbo
@file:setup_pct.py
@className:
@time:2019/2/14 10:37
@function:

"""
import subprocess
import os
import sys
import time
import psutil
import shutil
import traceback
from CaseRealization.Public.read_ini import ConfigRead
from CaseRealization.Public.get_new_version import CGetNewVersion
from CaseRealization.Public.get_app_path import CRead_regedit


def setup_ere(package_path, language, start=True):
    """
    静默安装pct
    :param package_path: 安装包路劲
    :param language: 安装语言
    :return: None
    """
    clear_environment()
    order = "{0} /verysilent /LANG={1} /NORESTART".format(package_path, language)
    p = subprocess.Popen(order, stdout=subprocess.PIPE)
    time_start = time.time()
    while True:
        if subprocess.Popen.poll(p) in (0, -1):
            break
        try:
            if not Process_is_exist(p.pid):
                break
        except:
            return False
        if (time.time() - time_start) > 300:
            try:
                os.kill(p.pid, 9)
            except:
                pass
            return False
        time.sleep(1)
    system_root = os.getenv('APPDATA')[0:3]
    print(system_root)
    tim_begin = time.time()
    pct_main_path_x64 = os.path.join(system_root, r"Program Files (x86)\EaseUS\RecExperts\bin\RecExperts.exe")
    pct_main_path_x86 = os.path.join(system_root, r"Program Files\EaseUS\RecExperts\bin\RecExperts.exe")
    while True:
        if os.path.exists(pct_main_path_x64):
            break
        elif os.path.exists(pct_main_path_x86):
            break
        elif (time.time() - tim_begin) > 60:
            return False
        time.sleep(10)
    if start:
        os.popen(pct_main_path_x64)
        time_start = time.time()
        while (time.time() - time_start) < 120:
            pct_main = get_pid_by_name("RecExperts")
            if pct_main:
                break
            time.sleep(10)
    return True


def get_pid_by_name(process_name):
    """
    通过进程名查找pid
    :param process_name: 进程名
    :return: pic
    """
    for item in psutil.pids():
        try:
            if process_name in psutil.Process(item).name():
                return item
        except:
            continue
    return None


def get_pid_list_name(process_name_list):
    """
    通过进程名查找pid
    :param process_name: 进程名列表，名称完成匹配
    :return: pidlist
    """
    pid_list = []
    for item in psutil.pids():
        try:
            if psutil.Process(item).name() in process_name_list:
                pid_list.append(item)
        except:
            continue
    return pid_list


def Process_is_exist(pid):
    """
    判断进程是否存在
    :param pid:
    :return:
    """
    pid_list = psutil.pids()
    if pid in pid_list:
        return True
    return False


def clear_environment(app_name="RecExperts.exe"):
    """
    安装前清除环境，包括原来的安装文件
    :return: None
    """
    kill_list = ["MediaPlayer.exe", "AliyunWrapExe.exe"]
    if isinstance(app_name, str):
        kill_list.append(app_name)
    elif isinstance(app_name, list):
        kill_list = kill_list + app_name
    pid_list = get_pid_list_name(kill_list)
    for one in pid_list:
        try:
            os.kill(one, 9)
        except:
            continue
    # install_local = Get_pct_install_local()
    # if install_local != "" and os.path.exists(install_local):
    #     try:
    #         shutil.rmtree(install_local)
    #     except:
    #         pass


def Get_pct_uninstall_local():
    """
    获取卸载pct的路劲
    :return:
    """
    # regedit_key = r"HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    my_re = CRead_regedit()
    pct_info = my_re.Get_app_info("EaseUS Todo PCTrans 11.0")
    print(pct_info)
    if not pct_info or "UninstallString" not in list(pct_info.keys()):
        return ""
    uninstall_path = pct_info["UninstallString"].strip().strip('"')
    if os.path.exists(uninstall_path):
        return uninstall_path
    return ""


def Get_pct_install_local():
    """
    获取安装路径
    :return:
    """
    # regedit_key = r"HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\"
    my_re = CRead_regedit()
    pct_info = my_re.Get_app_info("EaseUS Todo PCTrans 11.0")
    if not pct_info or "InstallLocation" not in list(pct_info.keys()):
        return ""
    uninstall_path = pct_info["InstallLocation"].strip().strip('"')
    if os.path.exists(uninstall_path):
        return uninstall_path
    return ""


def get_setup_info(is_antivirus=False):
    """
    获取安装包位置和安装语言
    :return: 安装包和语言
    """
    dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
    if is_antivirus:
        ini_file = os.path.join(dirname, r"Config\antivirus_config.ini")
    else:
        ini_file = os.path.join(dirname, r"Config\config.ini")
    if not os.path.exists(ini_file):
        raise Exception("ini file not exist!", ini_file)
    my_ini = ConfigRead()
    my_ini.GetData(ini_file)
    try:
        setup_version = my_ini.get("setup_version", "version")
        language = my_ini.get("language", "lang")
    except:
        raise Exception("get ini data failed!")
    # package_path = os.path.join(dirname, package_path)
    # if not os.path.exists(package_path):
    #     raise Exception("package not exists", package_path)
    if ";" in setup_version or ";" in language:
        setup_version_list = setup_version.split(";")
        language_list = language.split(";")
        return setup_version_list, language_list
    return setup_version, language


def Run_logic(ui=False):
    """
    安装流程
    :param ui:
    :return:
    """
    get_new = CGetNewVersion()
    local_path = get_new.Copy_version()
    setup_version, language = get_setup_info()
    if isinstance(setup_version, list):
        setup_version = setup_version[0]
    if isinstance(language, list):
        language = language[0]
    package_path = os.path.join(local_path, setup_version)
    clear_environment()
    install_times = 0
    while install_times < 4:
        install_times = install_times + 1
        if ui:
            if not Setup_logic_ui:
                return False
            if Setup_logic_ui(package_path, language):
                break
        else:
            if setup_pct(package_path, language, False):
                break
    if install_times >= 4:
        print("install failed")
        return False
    print("set up finish!")
    return True


if __name__ == '__main__':
    get_pid_list_name("")



