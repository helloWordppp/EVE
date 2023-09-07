# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import uiautomation

"""
@author:Pengbo
@file:EditMainUI.py
@className:
@Create Data:2023/9/6 9:15 14:08
@Description:

"""
import os
import time
import traceback
import sys
import json
from typing import Tuple
from copy import deepcopy
from collections import OrderedDict

from CaseRealization.Public.logging_print import MyLogPrint
from UI_Click.UIBase import CUIBase


class CEditMainUI(CUIBase):
    def __init__(self, time_out=60, my_log=None):
        """
        初始化
        :param window_name: 窗口的 Name
        :param window_classname: 窗口的 ClassName
        AutomationId: mainpage
        """
        self.dir_path, _ = os.path.split(sys.argv[0])
        if my_log is None:
            self.log_path = os.path.join(self.dir_path, "result", "log", "CEditMainUI.log")
            if not os.path.exists(os.path.split(self.log_path)[0]):
                os.makedirs(os.path.split(self.log_path)[0])
            self.log_path = os.path.join(self.dir_path, "result", "log", "CEditMainUI.log")
            self.my_log = MyLogPrint(self.log_path)
        else:
            self.my_log = my_log

        window_name, window_classname = "Video Editor", "QWidget"
        super(CEditMainUI, self).__init__(window_name, window_classname, time_out=time_out, my_log=self.my_log)

        self.main_product = self.get_project_main_ui(time_out)

        self.main_product.SetTopmost(True)

    def get_time_line_main_product(self) -> uiautomation.Control:
        """
        获取时间轴  控件的还在列表 第1，2-时间刻度  第3个左侧轨道头部分 第4个 轨道可导入素材部分 第5个撤销，分割等功能栏
        :return:
        """
        child_all = self.main_product.GetChildren()
        custom_control = None
        for item in child_all:
            if item.Name == "" and item.ControlTypeName == "CustomControl" and item.ClassName == "QSplitter":
                custom_control = item
        if custom_control is None:
            return None

        child_all = custom_control.GetChildren()
        time_line_group_control = None
        for item in child_all:
            if item.Name == "" and item.ControlTypeName == "GroupControl" and item.ClassName == "QWidget":
                time_line_group_control = item

        if time_line_group_control is None:
            return None

        return time_line_group_control

    def get_media_group_control(self) -> Tuple[uiautomation.Control, uiautomation.Control, uiautomation.Control]:
        """
        获取素材模块组控件
        :return:
        """
        child_all = self.main_product.GetChildren()
        self.my_log.print_info(child_all)
        custom_control = None
        for item in child_all:
            if item.Name == "" and item.ControlTypeName == "CustomControl" and item.ClassName == "QSplitter":
                custom_control = item
        if custom_control is None:
            return None

        child_all = custom_control.GetChildren()

        media_group_control = None
        for item in child_all:
            if item.Name == "" and item.ControlTypeName == "CustomControl" and item.ClassName == "QSplitter":
                media_group_control = item

        if media_group_control is None:
            return None

        child_all = media_group_control.GetChildren()

        media_group_control = child_all[2]
        player_control = child_all[1]
        info_control = child_all[0]

        if media_group_control.ControlTypeName == player_control.ControlTypeName == info_control.ControlTypeName:
            return media_group_control, player_control, info_control
        return None, None, None

    def click_media_button(self, media_group_control, click_name="Media") -> bool:
        """
        根据传入的值类型
        :param media_group_control:
        :param click_name:
        :return:
        """
        try:
            print(media_group_control.GetChildren())
            all_check_box = media_group_control.GetChildren()[0].GetChildren()
            for item in all_check_box:
                self.my_log.print_info(item.Name, item.Name == click_name)
                if item.Name == click_name:
                    item.Click()
                    return True
            return False
        except:
            self.my_log.print_info(media_group_control.GetChildren())
            self.my_log.print_info(traceback.format_exc())
            return False

    def get_media_info_items(self, media_group_control) -> list[uiautomation.Control]:
        """
        获取所有list 控件
        :param media_group_control:
        :return:
        """
        all_list_control = []
        child_all = self.Get_all_child(media_group_control)
        for item in child_all:
            if item.ClassName == "QListView" and item.ControlTypeName == "ListControl":
                all_list_control.append(item)

        return all_list_control

    def get_time_line_pointer(self, time_line_group_control) -> Tuple[uiautomation.Control, uiautomation.Control]:
        """
        获取时间刻度
        :return:
        """
        try:
            time_line_control = time_line_group_control.GetChildren()[1]

            # 获取控件的位置
            # left, top, right, bottom = self.Get_control_local(time_line_control)

            # 获取指针控件
            pointer_control = time_line_control.GetChildren()[0]

            return pointer_control, time_line_control
        except:
            self.my_log.print_info(traceback.format_exc())
            return None, None

    def time_line_vertically_scroll_bar_move(self, value=100, direction=-1, number=1, click_scroll=(0, 0)) -> None:
        """
        时间轴纵向滚动条拖动
        :param value:
        :param direction:
        :param number:
        :param click_scroll:
        :return:
        """
        pass

    def time_line_orthogonal_scroll_bar_move(self, time_line_group_control, percentage=50) -> None:
        """
        时间轴横向滚动条拖动
        :param time_line_group_control:
        :param percentage:百分比
        :return:
        """
        try:
            scroll_bar = time_line_group_control.GetChildren()[3].GetChildren()[-1]
            if scroll_bar.ControlTypeName == "ScrollBarControl":
                self.my_log.print_info("移动横向滚动条", percentage)
                left, top, right, bottom = self.Get_control_local(scroll_bar)
                width = right - left
                height = bottom - top

                value = int(scroll_bar.GetRangeValuePattern().Value)
                maximum = int(scroll_bar.GetRangeValuePattern().Maximum)
                large_change = scroll_bar.GetRangeValuePattern().LargeChange

                target_value = int(percentage * maximum / 100)
                self.my_log.print_info("value, target_value, maximum, large_change", value, target_value, maximum, large_change)

                click_times = 0
                if value > target_value:
                    while value > target_value:
                        scroll_bar.Click(20, int(height/2))
                        value = int(scroll_bar.GetRangeValuePattern().Value)
                        click_times += 1
                        if click_times > int(maximum/large_change):
                            return False
                    return True

                click_times = 0
                while value < target_value:
                    scroll_bar.Click(width - 20, int(height / 2))
                    value = int(scroll_bar.GetRangeValuePattern().Value)
                    click_times += 1
                    if click_times > int(maximum / large_change):
                        return False
                return True
        except:
            self.my_log.print_info("移动横向滚动条失败:", percentage)
            self.my_log.print_info(traceback.format_exc())
        return False

    def set_one_track_visible(self, time_line_group_control, one_track_control) -> None:
        """
        判断某一个轨道是否可见 不可见则滚动 使得其可见
        :param time_line_group_control:
        :param one_track_control:
        :return:
        """
        time_line_group = time_line_group_control.GetChildren()[3]

        left, top, right, bottom = self.Get_control_local(time_line_group)
        left1, top1, right1, bottom1 = self.Get_control_local(one_track_control)
        self.my_log.print_info(left, top, right, bottom, "------one_track_control", left1, top1, right1, bottom1)
        if top1 >= top and bottom1 <= bottom:
            return None
        # time_line_group_control.Click()
        if bottom1 < top:
            while bottom1 < top:
                # 向上滑动
                self.scroll_bar_move(100, 1)
                left1, top1, right1, bottom1 = self.Get_control_local(one_track_control)
            return None

        while bottom1 > bottom:
            # 向下滑动
            self.scroll_bar_move(100, -1)
            left1, top1, right1, bottom1 = self.Get_control_local(one_track_control)

    def get_all_track_list(self, time_line_group_control) -> list[uiautomation.Control]:
        """
        获取所有轨道列表
        :param time_line_group_control:
        :return:
        """
        try:
            time_line_group = time_line_group_control.GetChildren()[3].GetChildren()[0].GetChildren()[0].GetChildren()[0]
            all_track_list = time_line_group.GetChildren()
            return all_track_list
        except:
            self.my_log.print_info(traceback.format_exc())
            return None

    def get_track_parent(self, time_line_group_control) -> uiautomation.Control:
        """
        获取轨道父节点
        :param time_line_group_control:
        """
        try:
            track_parent = time_line_group_control.GetChildren()[3].GetChildren()[0].GetChildren()[0]
            return track_parent
        except:
            self.my_log.print_info(traceback.format_exc())
        return None

    def get_track_item_local(self, track_pic: str, particle: int = 20, y: int = 10) -> list:
        """
        获取轨道图片中item的位置
        :param track_pic: 图片的位置
        :param particle: 每次移动的距离
        :param y: y的位置
        :return:
        """
        sp = self.get_pic_size(track_pic)
        x = 1

        all_rgb = OrderedDict()
        # time_start = time.time()
        image_data = self.get_image_data(track_pic)
        while x <= sp[1]:
            # print(x, y)
            one = self.get_pix_bgr(image_data, x=x, y=y)
            all_rgb[x] = one
            x += particle

        # self.my_log.print_info(time.time() - time_start)
        # self.my_log.print_info(all_rgb)
        all_item = self.fund_the_item_local_in_track(all_rgb)
        new_list = []
        for one_item in all_item:
            temp_dic = OrderedDict()
            temp_dic["start"] = list(one_item.keys())[0]
            temp_dic["end"] = list(one_item.keys())[-1]

            if temp_dic["start"] == temp_dic["end"]:
                continue

            new_list.append(deepcopy(temp_dic))

        return new_list

    def get_track_zoom_ratio(self, time_line_main_product, set_value=-1):
        """
        获取轨道缩放比例
        :return:
        """
        all_funiction_control = time_line_main_product.GetChildren()[-1]

        slider_control = all_funiction_control.GetChildren()[-2]

        present_value = int(slider_control.GetValuePattern().Value)
        # print(slider_control.GetRangeValuePattern().Value, slider_control.GetSelectionPattern(), slider_control.GetValuePattern().Value)

        self.my_log.print_info("get_track_zoom_ratio  get_track_zoom_ratio:", present_value)

        if set_value < 0:
            return present_value

        up_button = all_funiction_control.GetChildren()[-1]
        down_button = all_funiction_control.GetChildren()[-3]
        click_times = 1
        if present_value < set_value:
            while present_value < set_value:
                up_button.Click()
                present_value = int(slider_control.GetValuePattern().Value)
                click_times += 1
                if click_times > 100:
                    break
            return 0
        click_times = 1
        while present_value > set_value:
            down_button.Click()
            present_value = int(slider_control.GetValuePattern().Value)
            click_times += 1
            if click_times > 100:
                break
        return 0



