# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:clipboard.py
@className:
@time:2019/7/19 13:19
@function:
剪切板操作
"""
import win32clipboard as w
import win32con
import win32api
import pyperclip
import time
from ctypes import windll


def GetClipboard():
    """
    获取剪切板的值
    :return:
    """
    w.OpenClipboard()
    t = w.GetClipboardData(win32con.CF_TEXT)
    w.CloseClipboard()
    return t


def SetClipboard(aString):
    """
    设置剪切板的值
    :param aString:
    :return:
    """
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(win32con.CF_TEXT, aString)
    w.CloseClipboard()


def Send_ctrl_v(value):
    """
    模拟键盘按下ctrl+a ctrl+v
    :param value: 剪切板中的值  键码查询（https://www.cnblogs.com/hubgit/p/5794856.html）
    :return:
    """
    pyperclip.copy(value)  # 设置剪切伴的值
    tem_value = pyperclip.paste()  # 获取剪切板的值
    if tem_value != value:
        print("设置剪切板不成功")
        return False

    win32api.keybd_event(17, 0, 0, 0)
    win32api.keybd_event(65, 0, 0, 0)
    win32api.keybd_event(65, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放按键
    win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)

    win32api.keybd_event(17, 0, 0, 0)
    win32api.keybd_event(86, 0, 0, 0)
    win32api.keybd_event(86, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放按键
    win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)
    return True


def Send_F9():
    """

    :return:
    """
    # win32api.keybd_event(17, 0, 0, 0)
    win32api.keybd_event(120, 0, 0, 0)
    win32api.keybd_event(120, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放按键
    # win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)


def Send_ctrl_s():
    """
    ctrl  +   S
    :return:
    """
    win32api.keybd_event(17, 0, 0, 0)
    win32api.keybd_event(76, 0, 0, 0)
    win32api.keybd_event(76, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放按键
    win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)


def Click_enter():
    """
    模拟按下enter按钮
    :return:
    """
    win32api.keybd_event(13, 0, 0, 0)
    win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)


def click_mouse(x: int, y: int, click_type: str = "left") -> None:
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
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    else:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
