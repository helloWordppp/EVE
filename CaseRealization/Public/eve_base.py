# -*- coding:utf-8 -*-

import wmi
import pythoncom
import os
import time
import logging
import sys
import psutil
import shutil
import traceback
from collections import OrderedDict

"""
@author:Pengbo
@file:ere_base.py
@className:
@time:2019/7/19 10:04
@function:

"""
import chardet
import codecs
from copy import deepcopy
import threading
import json
from CaseRealization.Public.get_app_path import CRead_regedit
import sys
import subprocess
import pytesseract
import win32gui
import win32api
import cv2
import win32con
from typing import Tuple
from win32 import win32process
from ctypes import windll
from PIL import Image
import ctypes
import ctypes.wintypes
import pyautogui

from CaseRealization.Public.logging_print import MyLogPrint


def pb_log(func):
    def pb_log2(self, *args, **kwargs):
        self.my_log.print_info("begin run {0} args:{1}  kwargs:{2}".format(func.__name__, args, kwargs))
        result = func(self, *args, **kwargs)
        self.my_log.print_info(
            "end run {0} return_type:{1} return_value:{2}".format(func.__name__, type(result), result))
        return result
    return pb_log2


class CEVEBase(object):
    """

    """
    def __init__(self, my_log=None):
        # self.sys_root = os.getenv('APPDATA')[0:3]
        # self.big_partition = self.Get_max_free_partition()
        # self.setup_path = self.Get_setup_local()
        self.dir_path, _ = os.path.split(sys.argv[0])
        if my_log is None:
            self.log_path = os.path.join(self.dir_path, "result", "log", "CEVEBase.log")
            if not os.path.exists(os.path.split(self.log_path)[0]):
                os.makedirs(os.path.split(self.log_path)[0])
            self.my_log = MyLogPrint(self.log_path)
        else:
            self.my_log = my_log

        self.setting_json = self.get_setting_json_file_path()

    def Get_setup_local(self):
        """

        :return:
        """
        install_path = Get_pct_install_local()
        pct_main_path_x64 = os.path.join(install_path, r"bin\RecExperts.exe")

        if os.path.exists(pct_main_path_x64):
            return pct_main_path_x64
        return None

    def get_pid_by_name(self, process_name):
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

    def Clean_event(self):
        """
        删除原有的结果
        :return:
        """
        for item in os.listdir(os.path.join(self.dir_path, "result")):
            try:
                os.remove(os.path.join(os.path.join(self.dir_path, "result"), item))
            except:
                pass

    def get_pid_by_name(self, process_name):
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

    def Get_max_free_partition(self):
        """
        获取最大剩余空间
        :return:
        """
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

    def clear_environment(self):
        """
        安装前清除环境，包括原来的安装文件
        :return: None
        """
        pct_pid = self.get_pid_by_name("PCTrans")
        if pct_pid:
            os.kill(pct_pid, 9)
            time.sleep(5)
        pct_pid = self.get_pid_by_name("uetool")
        if pct_pid:
            os.kill(pct_pid, 9)
            time.sleep(5)

    def run_program(self, cmd_order: str) -> int:
        """
        运行一个进程并返回pid  如果pid为0表示失败
        :param cmd_order:
        :return:
        """
        try:
            cmd_order = '{0}'.format(cmd_order)
            process = subprocess.Popen(
                cmd_order,
                shell=False
                # stdin=subprocess.PIPE,
                # stdout=subprocess.PIPE
                # stderr=subprocess.PIPE
            )
            self.my_log.print_info(process.pid)
        except:
            self.my_log.print_info("运行程序失败")
            return 0

        return process.pid

    def kill_app(self, app_name: str = "RecExperts.exe") -> None:
        """
        杀掉指定的进程
        :param app_name:
        :return:
        """
        pid_list = self.get_pid_buy_name(app_name)
        for item in pid_list:
            try:
                os.kill(item, 9)
            except:
                self.my_log.print_info("kill error:", item)

    def get_pid_buy_name(self, process_name: str) -> list:
        """
        通过进程名称获取进程pid  不区分大小写
        :param process_name:
        :return:
        """
        pid_list = []
        for item in psutil.pids():
            try:
                if process_name.lower() in psutil.Process(item).name().lower():
                    pid_list.append(item)
            except:
                pass
        return pid_list

    def update_record_custom(self, record_mode=None, sound_type=None, input_device_name=None, output_device_name=None,
                             reduction=False, boost=False):
        """
        更新ERE录制模式，启动时设备选择，声音选择

        :param record_mode:录制模式  1-全屏  2-声音  3-游戏  4-摄像头  5-网页视频录制
        :param sound_type:1-系统声音   2-麦克风  3-系统声音和麦克风
        :param input_device_name:
        :param output_device_name:
        :param boost: 麦克风增强
        :param reduction: 麦克风降噪
        :return:
        """
        # 杀掉ere进程
        self.kill_app("RecExperts.exe")
        temp_dir = os.getenv("TEMP")
        ere_config_path = os.path.join(os.path.split(temp_dir)[0], "EaseUS", "EaseUS RecExperts")

        # 修改custom.json 修改ere启动时的录制模式以及选择的麦克风等设备
        ere_custom_json = os.path.join(ere_config_path, "custom.json")
        if not os.path.exists(ere_custom_json):
            raise Exception("配置文件custom.json 不存在.", ere_custom_json)
        with open(ere_custom_json, "r", encoding="utf-8") as file_hand:
            custom_json_data = json.loads(file_hand.read())
            # print(custom_json_data["sound"])  # 修改前的data数据
        if record_mode:
            if record_mode not in [1, 2, 3, 4, 5]:
                raise Exception("录制模式不正确")
            if record_mode == 5:
                custom_json_data["record"]["mode"] = 1
                custom_json_data["record"]["web"] = True
            else:
                custom_json_data["record"]["mode"] = record_mode  # 音频录制模式
                custom_json_data["record"]["web"] = False
        if sound_type:
            if sound_type not in [1, 2, 3]:
                raise Exception("声音录制模式不正确")
            custom_json_data["sound"]["type"] = sound_type  # 1只录制系统声音  2 只录制麦克风  3录制系统声音和麦克风
            if sound_type in [2, 3]:
                custom_json_data["sound"]["boost"] = boost
                custom_json_data["sound"]["reduction"] = reduction
        if input_device_name is not None:
            # 麦克风设备名称 如果是空则使用系统默认 扬声器同理
            custom_json_data["sound"]["microphone"] = input_device_name
        if output_device_name is not None:
            custom_json_data["sound"]["speaker"] = output_device_name

        # 写json文件
        with open(ere_custom_json, "w", encoding="utf-8") as file_hand:
            json.dump(custom_json_data, file_hand)

    def update_record_setting_file_save(self, save_path):
        """
        更新setting文件中的保存位置
        :param save_path:
        :return:
        """
        temp_dir = os.getenv("TEMP")
        ere_config_path = os.path.join(os.path.split(temp_dir)[0], "EaseUS", "EaseUS RecExperts")
        # 修改settings.json 文件，修改文件保存位置和文件格式
        ere_setting_json = os.path.join(ere_config_path, "settings.json")
        if not os.path.exists(ere_setting_json):
            raise Exception("setting file not find:{0}".format(ere_setting_json))

        with open(ere_setting_json, "r", encoding="utf-8") as file_hand:
            setting_json_data = json.loads(file_hand.read())
            # print(setting_json_data["audio-option"])
            # print(setting_json_data["base-option"])

        # 修改格式为WAV
        setting_json_data["audio-option"]["formats-select"] = "WAV"
        # 修改保存路径
        setting_json_data["base-option"]["output"] = save_path
        # 写json文件
        with open(ere_setting_json, "w", encoding="utf-8") as file_hand:
            json.dump(setting_json_data, file_hand)

        return True

    def get_record_file_from_log(self, start_time: int = 0, end_time: int = 0) -> str:
        """
        从日志中获取最后一次的录制文件名称
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return:
        """
        temp_dir = os.getenv("TEMP")
        ere_log_path = os.path.join(temp_dir, "RecExperts.log")
        if not os.path.exists(ere_log_path):
            raise Exception("log file not find {0}".format(ere_log_path))
        # print(Get_file_code(ere_log_path))
        # ere_log_path_new = os.path.join(temp_dir, "RecExperts_temp.log")
        # convert(ere_log_path, ere_log_path_new)

        with open(ere_log_path, "r", encoding='utf-16-le') as file1:
            all_data = file1.readlines()

        for i in range(1, len(all_data)):
            one_line = all_data[-1*i].strip("\n")

            if "[RecordSetting] outputFilePath" not in one_line:
                continue
            if ", T=" not in one_line:
                continue
            if 0 < start_time < end_time:
                file_time = one_line.split(", T=")[0].replace("[", "")[:19]
                time_init = time.mktime(time.strptime(file_time, "%Y-%m-%d %H:%M:%S"))
                print(time_init)
                if time_init > end_time or time_init < start_time:
                    return ""
            file_name = one_line.split("outputFilePath :")[1].strip()
            if os.path.exists(file_name):
                return file_name

        return ""

    def get_setting_json_file_path(self) -> str:
        """
        获取setting文件地址
        :return:
        """
        temp_dir = os.getenv("TEMP")
        ere_config_path = os.path.join(os.path.split(temp_dir)[0], "EaseUS", "EaseUS RecExperts")
        # 修改settings.json 文件，修改文件保存位置和文件格式
        ere_setting_json = os.path.join(ere_config_path, "settings.json")
        if not os.path.exists(ere_setting_json):
            # raise Exception("setting file not find:{0}".format(ere_setting_json))
            return ""

        return ere_setting_json

    def update_setting_video_option(self, formats_select="", quality_select="", frame_rate_select: int = 0,
                                    frame_rate_mode_select: int = -1, exaudo_select: str = ""):
        """
        修改setting文件中视频选择项的相关内容
        :param formats_select:
        :param quality_select:
        :param frame_rate_select:
        :param frame_rate_mode_select:
        :param exaudo_select:
        :return:
        """
        with open(self.setting_json, "r", encoding="utf-8") as file_hand:
            setting_json_data = json.loads(file_hand.read())

        if formats_select != "":
            if formats_select not in ["MP4", "MOV", "FLV", "MKV", "AVI", "GIF"]:
                raise Exception("Parameter error, formats_select")
            # 修改录制格式
            setting_json_data["video-option"]["formats-select"] = formats_select
        if quality_select != "":
            if quality_select not in ["High (Default)", "Original (High picture quality)", "Standard (Space saving)"]:
                raise Exception("Parameter error, quality_select")
            # 修改录制质量
            setting_json_data["video-option"]["quality-select"] = quality_select
        if frame_rate_select != 0:
            if frame_rate_select not in [1, 5, 10, 15, 20, 24, 25, 30, 50, 60, 90, 120, 144]:
                raise Exception("Parameter error, frame_rate_select")
            # 修改录制帧率
            setting_json_data["video-option"]["frame-rate-select"] = frame_rate_select
        if frame_rate_mode_select != -1:
            if frame_rate_mode_select not in [0, 1]:
                raise Exception("Parameter error, frame_rate_mode_select")
            # 修改录制帧率是固定帧率还是可变帧率
            setting_json_data["video-option"]["frame-rate-mode-select"] = frame_rate_mode_select
        if exaudo_select != "":
            if exaudo_select.upper() not in ["NONE", "MP3", "AAC", "WAV", "OGG", "WMA", "FLAC"]:
                raise Exception("Parameter error, exaudo_select", exaudo_select)
            # 单独保存录制文件
            setting_json_data["video-option"]["exaudo-select"] = exaudo_select

        # 写json文件
        with open(self.setting_json, "w", encoding="utf-8") as file_hand:
            json.dump(setting_json_data, file_hand)

    def update_setting_recording_option(self, gpu: bool = None):
        """
        修改recording-option 中的值
        :param gpu:
        :return:
        """
        with open(self.setting_json, "r", encoding="utf-8") as file_hand:
            setting_json_data = json.loads(file_hand.read())

        if gpu is not None:
            if gpu not in [True, False]:
                raise Exception("Parameter error, gpu")
            # 修改GPU开关
            setting_json_data["recording-option"]["gpu"] = gpu

        # 写json文件
        with open(self.setting_json, "w", encoding="utf-8") as file_hand:
            json.dump(setting_json_data, file_hand)

    def update_setting_base_option(self, save_path):
        """
        修改保存路径
        :return:
        """
        # 修改保存路径
        with open(self.setting_json, "r", encoding="utf-8") as file_hand:
            setting_json_data = json.loads(file_hand.read())
        # 修改保存位置
        setting_json_data["base-option"]["output"] = save_path

        # 写json文件
        with open(self.setting_json, "w", encoding="utf-8") as file_hand:
            json.dump(setting_json_data, file_hand)

    def get_app_install(self, app_display_name: str = "EaseUS RecExperts"):
        """
        获取ere的安装路径
        :param app_display_name:
        :return:
        """
        my_re = CRead_regedit()
        pct_info = my_re.Get_app_info(app_display_name)
        if not pct_info or "InstallLocation" not in list(pct_info.keys()):
            return ""
        uninstall_path = pct_info["InstallLocation"].strip().strip('"')
        if os.path.exists(uninstall_path):
            return uninstall_path
        return ""

    def click_mous(self, x: int, y: int, click_type: str = "left") -> None:
        """
        移动鼠标到指定区域点击
        :param x: 起点x
        :param y: 起点y
        :return:
        """
        windll.user32.SetCursorPos(x, y)
        time.sleep(0.1)
        if click_type == "right":
            # 按下鼠标左键
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        else:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def double_click_mous(self, x: int, y: int, click_type: str = "left") -> None:
        """
        移动鼠标到指定区域点击
        :param x: 起点x
        :param y: 起点y
        :return:
        """
        time.sleep(1)
        windll.user32.SetCursorPos(x, y)
        time.sleep(0.5)
        if click_type == "right":
            # 按下鼠标左键
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN | win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN | win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        else:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def screen_capture(self, file_path, x=0, y=0, w=0, h=0):
        """
        截取屏幕截图，默认截取全屏
        :param file_path: 文件保存全路径
        :param x: 截图起始点x
        :param y: 截图起始点y
        :param w: 截图宽
        :param h: 截图高
        :return:
        """
        if w == 0 and h == 0:
            w, h = pyautogui.size()
        img = pyautogui.screenshot(region=[x, y, w, h])  # x,y,w,h
        # img.save('screenshot.png')
        # img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
        img.save(file_path)

    def get_app_window_hwnd(self, process_name="RecExperts.exe", all_handle=False):
        """
        获取窗口位置
        :return:
        """
        pid = self.get_pid_buy_name(process_name)
        if pid.__len__() == 0:
            raise Exception("not find process:{0}".format(process_name))
        process_handle_list = []
        process_handle = OrderedDict([("hwnd", 0), ("title", ""), ("hwnd_id", 0)])

        def get_all_hwnd(hwnd, mouse):
            """"""
            # if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
                nID = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    if nID[1] in pid:
                        process_handle["hwnd_id"] = nID[0]
                        process_handle["title"] = win32gui.GetWindowText(hwnd)
                        process_handle["hwnd"] = hwnd
                        self.my_log.print_info(process_handle)
                        process_handle_list.append(deepcopy(process_handle))
                except:
                    print(traceback.format_exc())

        win32gui.EnumWindows(get_all_hwnd, 0)

        if process_handle["hwnd"] == 0:
            raise Exception(f"not find window hwnd:{0}".format(process_name=process_name))
        if all_handle:
            return process_handle_list
        return process_handle["hwnd"]

    def get_ere_player_handle(self):
        """
        获取evw主界面handle
        """
        evw_handle = 0
        max_w = 0
        max_h = 0

        process_handle_list = self.get_app_window_hwnd(all_handle=True)

        for one_handle in process_handle_list:
            w, h = self.get_app_size(one_handle["hwnd"])
            # print(w, h)
            if w % 1240 == 0 and h % 604 == 0:
                evw_handle = one_handle["hwnd"]
                max_w = deepcopy(w)
                max_h = deepcopy(h)
        self.my_log.print_info("get_ere_player_handle hwnd is:{0} max_w:{1} max_h:{2}".format(evw_handle, max_w, max_h))
        return evw_handle

    def get_eve_edit_ui_handle(self):
        """
        获取eve编辑主界面handle
        :return:
        """
        evw_handle = 0
        max_w = 0
        max_h = 0

        process_handle_list = self.get_app_window_hwnd(process_name="VideoEditorQt.exe", all_handle=True)

        for one_handle in process_handle_list:
            w, h = self.get_app_size(one_handle["hwnd"])
            # print(w, h)
            if w % 946 == 0 and h % 337 == 0:
                evw_handle = one_handle["hwnd"]
                max_w = deepcopy(w)
                max_h = deepcopy(h)
        self.my_log.print_info("get_ere_home_handle hwnd is:{0} max_w:{1} max_h:{2}".format(evw_handle, max_w, max_h))
        return evw_handle

    def get_window_rect(self, hwnd) -> tuple:
        """
        通过hwnd获取窗口位置
        :param hwnd:
        :return:
        """
        try:
            f = ctypes.windll.dwmapi.DwmGetWindowAttribute
        except WindowsError:
            f = None
        if f:
            rect = ctypes.wintypes.RECT()
            DWMWA_EXTENDED_FRAME_BOUNDS = 9
            f(ctypes.wintypes.HWND(hwnd),
              ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
              ctypes.byref(rect),
              ctypes.sizeof(rect)
              )
            return rect.left, rect.top, rect.right, rect.bottom
        return 0, 0, 0, 0

    def get_app_size(self, hwnd) -> tuple:
        """
        返回界面大小
        :return:
        """
        try:
            # hwnd = self.get_app_window_hwnd()
            left, top, right, bottom = self.get_window_rect(hwnd)
            w = right - left
            h = bottom - top
        except:
            self.my_log.print_info(traceback.format_exc())
            return (0, 0)

        return (w, h)

    def get_app_screen(self, file_path, set_top=False, hwnd=0) -> None:
        """
        获取窗口截图
        :return:
        """
        w = 0
        h = 0
        try:
            if hwnd == 0:
                hwnd = self.get_app_window_hwnd()
            left, top, right, bottom = self.get_window_rect(hwnd)
            w = right-left
            h = bottom-top
            if set_top:
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        except:
            self.my_log.print_info(traceback.format_exc())
            left, top, right, bottom = 0, 0, 0, 0
        # print(left, top, right, bottom)
        self.screen_capture(file_path, left, top, w, h)

    def get_app_screen_2(self, file_path, reg=(1950, 380), size=(434, 58), handle=None):
        """
        截取指的区域的截图，如果handle为空则使用相对位置，如果不为空则使用绝对位置
        :param file_path:
        :param reg:
        :param size:
        :param handle:
        :return:
        """
        # self.my_log.print_info(reg, size)
        w = 0
        h = 0
        try:
            if handle is None:
                hwnd = self.get_app_window_hwnd()
                left, top, right, bottom = self.get_window_rect(hwnd)

                left = left + reg[0]
                top = top + reg[1]

                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            else:
                left = reg[0]
                top = reg[1]

        except:
            self.my_log.print_info(traceback.format_exc())
            left, top, right, bottom = 0, 0, 0, 0
            return False
        # print(left, top, right, bottom, "---------------1")
        try:
            self.screen_capture(file_path, left, top, size[0], size[1])
        except:
            time.sleep(0.5)
            self.my_log.print_info(file_path)
            self.my_log.print_info(traceback.format_exc())
            try:
                self.screen_capture(file_path, left, top, size[0], size[1])
            except:
                self.my_log.print_info(file_path)
                self.my_log.print_info(traceback.format_exc())
                return False
        return True

    def get_text_from_image(self, image):
        """
        从图片获取文本
        :param image:
        :return:
        """
        # 设置 Tesseract OCR 的位置
        dir_path, _ = os.path.split(sys.argv[0])
        orc_path = os.path.join(dir_path, "res", "Tesseract-ORC", "tesseract.exe")
        if os.path.exists(orc_path):
            pytesseract.pytesseract.tesseract_cmd = orc_path
        elif os.path.exists(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"):
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        elif os.path.exists(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"):
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


        # img = Image.open(r'E:\MyProject\PythonProject\EaseUSVoiceWave\temp\app_screen\Arena.png')
        # img = cv2.imread(r'E:\MyProject\PythonProject\EaseUSVoiceWave\temp\app_screen\Arena.png')
        img = cv2.imread(image)

        # 进行 OCR 识别
        # text = pytesseract.image_to_string(img)

        # 获取图片尺寸
        height, width, _ = img.shape
        select_name = pytesseract.image_to_string(img)
        select_name = select_name.strip()

        return select_name

    def compare_images(self, image1_path, image2_path):
        """
        对比图片相似度
        :param image1_path:
        :param image2_path:
        :return:
        """
        # 打开图片
        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)

        # 转换为灰度图像
        image1 = image1.convert('L')
        image2 = image2.convert('L')

        # 计算直方图
        hist1 = image1.histogram()
        hist2 = image2.histogram()

        # 计算两个直方图的相似度
        sum1 = 0
        sum2 = 0
        sum3 = 0
        for i in range(len(hist1)):
            sum1 += (hist1[i] - hist2[i]) ** 2
            sum2 += hist1[i]
            sum3 += hist2[i]
        similarity = sum1 / (2 * sum2 * sum3)

        return similarity

    def scroll_bar_move(self, value=100, direction=-1, number=1, click_scroll=(0, 0)) -> None:
        """
        滚动鼠标
        :param value:滚动的值
        :param direction: -1向下  1向上
        :param number: 滚动次数 默认2次
        :param click_scroll: 滚动前是否点击，如果是0则不点击,值为相对主界面左顶点位置  默认值为放大1倍的值
        :return:
        """
        if click_scroll[0] != 0:
            x = click_scroll[0]
            y = click_scroll[1]
            self.click_mous(x, y)
            time.sleep(0.5)
        for i in range(number):
            pyautogui.scroll(direction*value)
            time.sleep(0.1)

    def drag_drop_mouse(self, x1, y1, x2, y2, duration=0.5, button='left') -> None:
        """
            鼠标移动到x1，y1然后鼠标按住left拖动至x2，y2 用时0.5秒
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :param duration:用时0.5秒
        :param button:left
        :return:
        """
        pyautogui.moveTo(x1, y1)
        pyautogui.dragTo(x2, y2, duration=duration, button=button)  # 按住鼠标左键，用0.5s将鼠标拖拽至1230，458

    def get_img_local(self, voice_box_ico, app_pic) -> tuple:
        """
        通过图标获取图片中是否包含该图标，如果包含则返回位置
        :param voice_box_ico:
        :param app_pic:
        :return:
        """
        # 将图片背景进行修改 提高对比成功率
        # voice_box_ico = self.convert_img_background(voice_box_ico)
        # print(haystackImage)
        voice_location = pyautogui.locate(voice_box_ico, app_pic, grayscale=False, confidence=0.8)

        if voice_location is None:
            return 0, 0
        x, y = pyautogui.center(voice_location)  # 转化为 x,y坐标
        return x, y

    def conversion_image_size(self, image_path, width, height):
        """
        转换图片大小
        :param image_path:
        :param width:
        :param height:
        :return:
        """
        temp_image_dir = os.path.join(self.dir_path, "temp", "temp_image_dir")
        if not os.path.exists(temp_image_dir):
            os.makedirs(temp_image_dir)

        file_name = os.path.split(image_path)[1]
        file_name = os.path.splitext(file_name)[0] + ".png"
        new_image_path = os.path.join(temp_image_dir, file_name)
        # self.my_log.print_info(new_image_path, image_path_new)
        if os.path.exists(new_image_path):
            os.remove(new_image_path)

        img = cv2.imread(image_path, -1)  # 读取图片。-1将图片透明度传入，数据由RGB的3通道变成4通道

        res = cv2.resize(img, (width, height), interpolation=cv2.INTER_CUBIC)  # 改变图片大小
        cv2.imwrite(new_image_path, res)  # 保存图片，文件名自定义，也可以覆盖原文件

        return new_image_path

    def get_pic_size(self, pic_path):
        """
        获取图片宽高
        :param pic_path:
        :return:
        """
        img = cv2.imread(pic_path)  # 读取图片信息

        # sp = img.shape[0:2]     #截取长宽啊
        sp = img.shape  # [高|宽|像素值由三种原色构成]
        width = sp[0]
        height = sp[1]

        return width, height

    def set_app_top(self, set_top: bool = True, hwnd: int = None):
        """
        页面设置top
        """
        try:
            if hwnd is None:
                hwnd = self.get_app_window_hwnd()
            if set_top:
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            else:
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        except:
            self.my_log.print_info(traceback.format_exc())

    def scroll_bar_move(self, value=100, direction=-1, number=1, click_scroll=(0, 0)) -> None:
        """

        :param value:滚动的值
        :param direction: -1向下  1向上
        :param number: 滚动次数 默认2次
        :param click_scroll: 滚动前是否点击，如果是0则不点击,值为相对主界面左顶点位置  默认值为放大1倍的值
        :return:
        """
        if click_scroll[0] != 0:
            left, top, right, bottom = self.get_window_rect(self.hwnd)
            x = click_scroll[0]*self.big_size + left
            y = top+click_scroll[1]*self.big_size
            self.click_mous(x, y)
            time.sleep(0.5)
        for i in range(number):
            pyautogui.scroll(direction*value)
            time.sleep(0.1)

    def get_image_data(self, image_path):
        ext = os.path.basename(image_path).strip().split('.')[-1]
        if ext not in ['png', 'jpg']:
            raise Exception('format error')
        img = cv2.imread(image_path)
        return img

    # 获取图片坐标bgr值
    def get_pix_bgr(self, image_data, x: int, y: int) -> Tuple[int, int, int]:
        """
        返回图片某一个点的rgb值   如果位置超过图片则会出现异常
        :param image_path:
        :param x:
        :param y:
        :return:
        """
        # image_data = cv2.imread(image_path)

        # px = image_data[x, y]
        blue = image_data[y, x, 0]
        green = image_data[y, x, 1]
        red = image_data[y, x, 2]
        return red, green, blue

    def get_pic_size(self, image_path: str) -> Tuple[int, int, int]:
        """
        获取图片尺寸
        :param image_path:
        :return:
        """
        ext = os.path.basename(image_path).strip().split('.')[-1]
        if ext not in ['png', 'jpg']:
            raise Exception('format error')
        img = cv2.imread(image_path)
        return img.shape  # [高|宽|像素值由三种原色构成]

    def fund_the_item_local_in_track(self, all_rgb: OrderedDict, no_item_rgb=(23, 33, 41)) -> OrderedDict:
        """
        通过获取到的颜色点位，大致判断出轨道上item的起始和结束位置 该位置与all_rgb中的位置精度有关
        该位置为相对于图片的位置
        :param all_rgb:
        :param no_item_rgb: 没有节点时轨道的颜色值 判断是会允许有左右10个值的浮动
        :return:
        """
        all_item = []
        one_item = OrderedDict()
        for x in all_rgb.keys():
            if no_item_rgb[0] - 10 <= all_rgb[x][0] <= no_item_rgb[0] + 10 and \
                    no_item_rgb[1] - 10 <= all_rgb[x][1] <= no_item_rgb[1] + 10 and \
                    no_item_rgb[2] - 10 <= all_rgb[x][2] <= no_item_rgb[2] + 10:
                if len(one_item.keys()) > 0:
                    all_item.append(one_item)
                one_item = OrderedDict()
                continue
            else:
                one_item[x] = all_rgb[x]

        if len(one_item.keys()) > 0 and one_item not in all_item:
            all_item.append(one_item)

        # print(all_item)
        return all_item

    def get_ui_big(self):
        """
        获取界面的放大倍数
        :return:
        """
        w, h = pyautogui.size()
        if w > 2560:
            return 2
        return 1



def convert(source, out_put, in_enc="utf-16-le", out_enc="UTF-8"):
    """
    该程序用于将目录下的文件从指定格式转换到指定格式，默认的是GBK转到utf-8
    :param file:    文件路径
    :param in_enc:  输入文件格式
    :param out_enc: 输出文件格式
    :return:
    """
    in_enc = in_enc.upper()
    out_enc = out_enc.upper()
    if os.path.exists(out_put):
        os.remove(out_put)
    try:
        print("convert [ " + source.split('\\')[-1] + " ].....From " + in_enc + " --> " + out_enc )
        f = codecs.open(source, 'r', in_enc)
        new_content = f.read()
        codecs.open(out_put, 'w', out_enc).write(new_content)
    # print (f.read())
    except IOError as err:
        print("I/O error: {0}".format(err))



def Get_file_code(path):
    """
    获取文档的编码类型，如果失败则返回none
    :param path:文件路径
    :return:文件编码
    """
    with open(path, 'rb') as file:
        data = file.read(20000)
        dicts = chardet.detect(data)
    file_code = dicts["encoding"]
    if "utf-16-le" in file_code.lower():
        file_code = "utf-16"
    return file_code


def Copy_pct_log(new_file_path):
    """
    由于pct的日志时一个大小不超过6MB的日志，因此为了保留之前的日志，从而编写一个日志增量的方法
    :return:
    """
    tem_path = os.getenv('TEMP')
    log_file = os.path.join(tem_path, "todoPCTrans.log")
    if not os.path.exists(new_file_path):
        try:
            shutil.copy(log_file, new_file_path)
        except:
            return False
        return True
    log_file_size = os.path.getsize(log_file)
    file_size = os.path.getsize(new_file_path)

    log_file_code = Get_file_code(log_file)
    my_log_file_code = Get_file_code(new_file_path)

    # if (log_file_size - old_log_file_size) < 1024 * 10:
    #     return True
    # my_log_file_code = "utf-16-le"
    if my_log_file_code:
        file_handle = open(new_file_path, "a+", encoding=my_log_file_code)
    else:
        file_handle = open(new_file_path, "a+", encoding="utf-16")

    lase_line = Get_last_line(file_handle, file_size)
    try:
        last_time = time.mktime(time.strptime(lase_line[:19], "%Y-%m-%d %H:%M:%S"))
    except:
        last_time = time.time()

    is_new = False
    # print("log_file_code", log_file_code)
    # log_file_code = "utf-16-le"
    if log_file_code:
        log_file_handle = open(log_file, "r", encoding=log_file_code)
    else:
        log_file_handle = open(log_file, "r", encoding="utf-16")
    read_count = 0
    while True:
        try:
            line = log_file_handle.readline()
            read_count += 1
        except:
            print(traceback.format_exc())
            print("------Copy_pct_log---read_count:{0}".format(read_count))
            continue
        if not line:
            break
        try:
            line = line.replace('\n', '').replace('\r', '').strip()
            if not is_new:
                temp_time = time.mktime(time.strptime(line[:19], "%Y-%m-%d %H:%M:%S"))
        except Exception:
            continue
        if temp_time > last_time:
            is_new = True
        # print(temp_time, last_time)
        if is_new:
            file_handle.write(line+"\n")

    file_handle.close()
    log_file_handle.close()
    return True


def Get_last_line(file_handle, file_size):
    """
    获取文件的最后一行
    :param file_handle:
    :param file_size:
    :return:
    """
    block_size = 1024
    if file_size <= 1024:
        all_line = file_handle.readlines()
        for index in range(0, len(all_line)):
            if all_line[len(all_line)-1-index] != "" and all_line[len(all_line)-1-index] != b'\r\n':
                return all_line[len(all_line)-1-index]
        return None

    maxseekpoint = (file_size/block_size)  # 这里的除法取的是floor
    last_line = None
    while True:
        maxseekpoint -= 1
        try:
            file_handle.seek(maxseekpoint * block_size)
            lines = file_handle.readlines()
            if lines.__len__() > 2:
                for index in range(0, len(lines)):
                    temp = lines[len(lines) - 1 - index]
                    temp = temp.replace('\n', '').replace('\r', '')
                    temp = temp.strip()
                    if temp != '':
                        last_line = lines[len(lines) - 1 - index]
                        break
                break
        except:
            print(traceback.format_exc())
            break
    # print(last_line)
    return last_line


def clear_environment(app_name=None):
    """
    安装前清除环境，包括原来的安装文件
    :return: None
    """
    kill_list = ["_iu14D2N.tmp", "unins000.exe", "PCTrans.exe", "uetool.exe", "uexperice.exe", "uexperice.exe"]
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


def Delect_install_path():
    """
    删除安装目录
    :return:
    """
    install_local = Get_pct_install_local()
    if install_local != "" and os.path.exists(install_local):
        try:
            shutil.rmtree(install_local)
        except:
            pass


def Get_pct_uninstall_local():
    """
    获取卸载pct的路劲
    :return:
    """
    # regedit_key = r"HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\EaseUS Todo PCTrans_is1"
    my_re = CRead_regedit()
    pct_info = my_re.Get_app_info("EaseUS Todo PCTrans 11.0")
    print(pct_info)
    if not pct_info or "UninstallString" not in list(pct_info.keys()):
        return ""
    uninstall_path = pct_info["UninstallString"].strip().strip('"')
    if os.path.exists(uninstall_path):
        return uninstall_path
    return ""


def Get_pct_install_regedit():
    """
    获取pct的安装注册表信息
    :return:
    """
    my_re = CRead_regedit()
    pct_info = my_re.Get_app_info("EaseUS Todo PCTrans 11.0")
    print(pct_info)

    return pct_info


def Get_chrome_install_regedit():
    """
    获取pct的安装注册表信息
    :return:
    """
    my_re = CRead_regedit()
    pct_info = my_re.Get_app_info("chrome")
    print(pct_info)

    return pct_info


def Get_pct_install_local():
    """
    获取安装路径
    :return:
    """
    # regedit_key = r"HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\EaseUS Todo PCTrans_is1"
    my_re = CRead_regedit()
    pct_info = my_re.Get_app_info("EaseUS Todo PCTrans")
    if not pct_info or "InstallLocation" not in list(pct_info.keys()):
        return ""
    uninstall_path = pct_info["InstallLocation"].strip().strip('"')
    if os.path.exists(uninstall_path):
        return uninstall_path
    return ""


def get_pid_by_name(process_name):
    """
    通过进程名查找pid
    :param process_name: 进程名
    :return: pic
    """
    for item in psutil.pids():
        try:
            if psutil.Process(item).name() in process_name:
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


class CCopy_log(threading.Thread):
    """
    日志拷贝线程
    """
    def __init__(self, new_file_path, my_set):
        super(CCopy_log, self).__init__()
        self.new_file_path = new_file_path
        self.my_set = my_set

    def run(self):
        time_begin = time.time()
        while True:
            try:
                if (time.time() - time_begin) > 30:
                    Copy_pct_log(self.new_file_path)
                    time_begin = time.time()
                if self.my_set.isSet():
                    Copy_pct_log(self.new_file_path)
                    break
                time.sleep(5)
            except:
                print(traceback.format_exc())


if __name__ == '__main__':
    start_time = time.time()
    print(10%5)
    print(2480/2, 1208/2)
    # test = CEREBase()
    # # print(test.get_record_file_from_log())
    # # time.sleep(30)
    # end_time = time.time()
    # # print(test.get_record_file_from_log(start_time, end_time))
    # handle = test.get_app_window_hwnd()
    # test.get_app_screen()


