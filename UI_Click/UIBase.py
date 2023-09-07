# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:UIBase.py
@className:
@Create Data:2023/6/19 17:10 14:08
@Description:

"""
import os
import time
import sys
from collections import OrderedDict
import traceback
import uiautomation
from ctypes import windll

from CaseRealization.Public.eve_base import CEVEBase
from CaseRealization.Public.clipboard import Send_ctrl_v
from CaseRealization.Public.logging_print import MyLogPrint


class CUIBase(CEVEBase):
    def __init__(self, window_name, window_classname, time_out=60, my_log=None):
        """
        初始化
        :param window_name: 窗口的 Name
        :param window_classname: 窗口的 ClassName
        AutomationId: mainpage
        """
        self.dir_path, _ = os.path.split(sys.argv[0])
        if my_log is None:
            self.log_path = os.path.join(self.dir_path, "result", "log", "CUIBase.log")
            if not os.path.exists(os.path.split(self.log_path)[0]):
                os.makedirs(os.path.split(self.log_path)[0])
            self.log_path = os.path.join(self.dir_path, "result", "log", "CUIBase.log")
            self.my_log = MyLogPrint(self.log_path)
        else:
            self.my_log = my_log

        super(CUIBase, self).__init__(my_log)

        self.window_name = window_name
        self.window_class_name = window_classname

        self.main_product = None
        # self.main_product = self.Get_main_handle(time_out=time_out)
        # if not self.main_product:
        #     print("主程序窗口未找到，无法进行后续流程")
        #     self.main_product = None
        #     # raise Exception("主程序窗口未找到，无法进行后续流程")
        # else:
        #     self.main_product.SetTopmost(True)
        #     pass

    def rename_video(self, file_name, video_index=0) -> bool:
        """
        重命名播放器中的第一视频
        :param file_name:文件名称 不带后缀
        :param video_index: 默认第一个文件
        :return:
        """
        # 获取床后hanle
        ere_handle = self.get_ere_player_handle()
        # ere_handle = self.get_app_window_hwnd(process_name="RecExperts.exe")
        if ere_handle == 0:
            self.my_log.print_info("没有找到播放器窗口")
            return False

        # 将应用置顶显示
        self.set_app_top(set_top=True, hwnd=ere_handle)
        time.sleep(2)

        # 获取界面大小
        width, height = self.get_app_size(ere_handle)

        ui_big = 1
        if width > 2000:
            ui_big = 2
        elif width > 3000:
            ui_big = 3
        # 根据界面大小判断是否是进入播放器
        if height < 500*ui_big:
            self.my_log.print_info("获取播放器界面高度不正确")
            return False

        # 获取界面位置左上角顶点位置
        left, top, right, bottom = self.get_window_rect(ere_handle)

        # 点击视频列表的第一个视频
        self.click_mous(x=left+1039*ui_big, y=top+153*ui_big+96*ui_big*video_index)
        time.sleep(0.5)

        # 点击rename按钮
        self.click_mous(x=left + 1026 * ui_big, y=top + 576 * ui_big)
        time.sleep(0.5)

        # 设置剪切版 发送ctrl+v事件
        Send_ctrl_v(file_name)
        time.sleep(0.5)

        # 点击空白区域生效
        self.click_mous(x=left + 934 * ui_big, y=top + 580 * ui_big)
        time.sleep(0.5)

        # 将应用置顶显示取消
        self.set_app_top(set_top=False, hwnd=ere_handle)

        return True

    def find_repair_ui_home(self) -> int:
        """
        在主界面查找是否有修复按钮
        :return:返回非0标识失败
        """
        # 获取床后hanle

        ere_handle = self.get_ere_home_handle()
        if ere_handle == 0:
            self.my_log.print_info("获取主界面失败")
            return -1

        # 将应用置顶显示
        self.set_app_top(set_top=True, hwnd=ere_handle)
        time.sleep(2)

        # 获取界面位置左上角顶点位置
        left, top, right, bottom = self.get_window_rect(ere_handle)

        # 获取界面大小
        width, height = self.get_app_size(ere_handle)

        ui_big = 1
        if width > 1000:
            ui_big = 2
        elif width > 2000:
            ui_big = 3
        if height > 400 * ui_big:
            self.my_log.print_info("not in home ui")
            self.set_app_top(set_top=False, hwnd=ere_handle)
            return 1

        # 转换损坏图标的宽高
        damaged_pic = os.path.join(self.dir_path, "res", "case_uibise", "home_repair.png")
        if not os.path.exists(damaged_pic):
            self.set_app_top(set_top=False, hwnd=ere_handle)
            raise Exception("file not find", damaged_pic)
        height, width = self.get_pic_size(damaged_pic)
        new_damaged_pic = self.conversion_image_size(damaged_pic, width=int(width / 2) * ui_big,
                                                     height=int(height / 2) * ui_big)

        # 对主界面进行截图，并置顶显示
        main_ui_path = os.path.join(self.dir_path, "result", "case_repair", "main_ui_pic")
        if not os.path.exists(main_ui_path):
            os.makedirs(main_ui_path)
        ui_pci_name = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time())) + "_main_ui.png"
        ui_pci_name = os.path.join(main_ui_path, ui_pci_name)
        self.get_app_screen(file_path=ui_pci_name, set_top=True, hwnd=ere_handle)

        x, y = self.get_img_local(voice_box_ico=new_damaged_pic, app_pic=ui_pci_name)
        if x == 0 or y == 0:
            self.my_log.print_info("not find repair ui.")
            self.set_app_top(set_top=False, hwnd=ere_handle)
            return 2
        # 点击yes
        # self.click_mous(x=left+410*ui_big, y=top+270*ui_big)
        # 点击letter
        self.click_mous(x=left + 535 * ui_big, y=top + 270 * ui_big)
        self.set_app_top(set_top=False, hwnd=ere_handle)
        return 0

    def exit_ere(self):
        """
        通过界面关闭ERE
        :return:
        """
        ere_handle = self.get_ere_player_handle()
        if ere_handle != 0:
            self.set_app_top(set_top=True, hwnd=ere_handle)
            time.sleep(1)
            # 获取界面位置左上角顶点位置
            left, top, right, bottom = self.get_window_rect(ere_handle)

            # 获取界面大小
            width, height = self.get_app_size(ere_handle)

            ui_big = 1
            if width > 2000:
                ui_big = 2
            elif width > 3000:
                ui_big = 3

            self.click_mous(x=left + 1216 * ui_big, y=top + 23 * ui_big)
            time.sleep(3)

        ere_handle = self.get_ere_home_handle()
        if ere_handle != 0:
            self.set_app_top(hwnd=ere_handle)
            # 获取界面位置左上角顶点位置
            left, top, right, bottom = self.get_window_rect(ere_handle)

            # 获取界面大小
            width, height = self.get_app_size(ere_handle)

            ui_big = 1
            if width > 1000:
                ui_big = 2
            elif width > 2000:
                ui_big = 3

            self.click_mous(x=left + 906 * ui_big, y=top + 33 * ui_big)
            time.sleep(3)

    def get_select_video_name(self, video_index=0):
        """
        获取当前播放器选择的文件名称
        :return:
        """
        ere_handle = self.get_ere_player_handle()
        if ere_handle == 0:
            self.my_log.print_info("get player window failed.")
            return ""

        self.set_app_top(set_top=True, hwnd=ere_handle)
        time.sleep(1)
        # 获取界面位置左上角顶点位置
        left, top, right, bottom = self.get_window_rect(ere_handle)

        # 获取界面大小
        width, height = self.get_app_size(ere_handle)

        ui_big = 1
        if width > 2000:
            ui_big = 2
        elif width > 3000:
            ui_big = 3
        if video_index > 0:
            # 点击视频列表的第er个视频
            self.click_mous(x=left + 1039 * ui_big, y=top + 153 * ui_big + 96 * ui_big * video_index)
            time.sleep(2)

        # 截取播放器顶部
        temp_dir = os.path.join(self.dir_path, "result", "case_record_all_formats", "temp_pic")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        pic_name = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time())) + ".png"
        pic_name = os.path.join(temp_dir, pic_name)
        x = left + 144*ui_big
        y = top
        self.get_app_screen_2(pic_name, reg=(x, y), size=(750*ui_big, 41*ui_big), handle=ere_handle)
        file_name = self.get_text_from_image(pic_name)
        print(file_name)

        return file_name

    def get_reg_text(self, x, y, w, h):
        """
        对某一个区域进行截图，然后识别文字
        :param x:
        :param y:
        :return:
        """
        # 截取播放器顶部
        temp_dir = os.path.join(self.dir_path, "result", "case_record_all_formats", "temp_pic")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        pic_name = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time())) + ".png"
        pic_name = os.path.join(temp_dir, pic_name)
        if not self.get_app_screen_2(pic_name, reg=(x, y), size=(w, h), handle=1):
            return ""
        file_name = self.get_text_from_image(pic_name)
        self.my_log.print_info("get_reg_text", file_name)

        return file_name

    def click_camera_mord(self):
        """
        摄像头录制模式
        :return:
        """
        ere_handle = self.get_ere_home_handle()
        if ere_handle == 0:
            self.my_log.print_info("获取主界面失败")
            return -1

        # 将应用置顶显示
        self.set_app_top(set_top=True, hwnd=ere_handle)
        time.sleep(2)

        # 获取界面位置左上角顶点位置
        left, top, right, bottom = self.get_window_rect(ere_handle)

        # 获取界面大小
        width, height = self.get_app_size(ere_handle)

        ui_big = 1
        if width > 1000:
            ui_big = 2
        elif width > 2000:
            ui_big = 3
        if height > 400 * ui_big:
            self.my_log.print_info("not in home ui")
            self.set_app_top(set_top=False, hwnd=ere_handle)
            return 1

        # 点击翻页按钮
        self.click_mous(x=left + 41 * ui_big, y=top + 225 * ui_big)
        time.sleep(1)

        # 点击摄像头按钮
        self.click_mous(x=left + 41 * ui_big, y=top + 184 * ui_big)
        time.sleep(3)

        # self.set_app_top(set_top=False, hwnd=ere_handle)

        return 0

    def Get_main_handle(self, time_out=60):
        """
        获取主程序窗口的Control对象
        :return:
        """
        time_begin = time.time()
        main_product = None
        main_product_list = []
        desktop = uiautomation.GetRootControl()
        # all_child =
        while True:
            time.sleep(1)
            # uiautomation.WindowControl(searchDepth=1, ClassName="Qt5QWindow", Name=r"EaseUS Todo PCTrans")
            for one_child in desktop.GetChildren():
                try:
                    if one_child.Name == self.window_name and self.window_class_name in one_child.ClassName:
                        main_product = one_child
                        if main_product and main_product.Exists() and main_product.IsEnabled:
                            main_product_list.append(main_product)
                    if one_child.ClassName == "#32770" and one_child.Name == "tip":
                        try:
                            one_child.GetChildren()[0].Click()
                        except:
                            pass
                except:
                    pass
            if len(main_product_list) > 0:
                break
            if (time.time() - time_begin) > time_out:
                break
        return main_product_list

    def get_project_main_ui(self, time_out=30):
        """
        获取工程管理界面ui 取列表中最小的窗口
        这个地方会找到两个窗口一个是外部阴影窗口，因此选择时选择较小的窗口才是控件窗口
        :return:
        """
        all_main_handle = self.Get_main_handle(time_out=time_out)
        min_handle = None
        for item in all_main_handle:
            if min_handle is None:
                min_handle = item
                continue
            width, height = self.Get_control_size(item)
            width_m, height_m = self.Get_control_size(min_handle)
            if width < width_m and height < height_m:
                min_handle = item

        return min_handle

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

    def Get_control_size(self, control):
        """
        获取控件的大小
        :param control:
        :return: 宽 高
        """
        left = control.BoundingRectangle.left
        top = control.BoundingRectangle.top

        right = control.BoundingRectangle.right
        bottom = control.BoundingRectangle.bottom
        width = right - left
        height = bottom - top
        return width, height

    def Get_control_local(self, control):
        """
        获取控件的位置
        :param control:
        :return:
        """
        left = control.BoundingRectangle.left
        bottom = control.BoundingRectangle.bottom
        right = control.BoundingRectangle.right
        top = control.BoundingRectangle.top

        return left, top, right, bottom

    def Get_control_is_specified_size(self, control, width, height):
        """
        判断控件是否是指定的大小，或者是整数倍
        :param control:控件对象
        :param width:宽
        :param height:高
        :return:是 true
        """
        try:
            c_width, c_height = self.Get_control_size(control)
            if c_width == width and c_height == height:
                return True
            elif c_width > width and c_width%width == 0 and c_height%height == 0:
                return True
            return False
        except:
            return False

    def click_and_move(self, item_control, t_x, t_y):
        """
        点击一个控件并且移动到指定位置
        :return:
        """
        # 获取控件的位置
        x, y = item_control.MoveCursorToInnerPos()

if __name__ == '__main__':
    test = CUIBase()
    time.sleep(2)
    test.get_select_video_name(video_index=1)
    # time.sleep(5)
    # test.get_select_video_name()