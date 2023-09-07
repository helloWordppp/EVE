# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:move_random_item.py
@className:
@Create Data:2023/9/6 15:52 14:08
@Description:

"""
import os
import time
import traceback
import sys
import json
import random

from collections import OrderedDict

from CaseRealization.Public.logging_print import MyLogPrint
from UI_Click.EditMainUI.EditMainUI import CEditMainUI


class CMoveRandomItem(CEditMainUI):
    def __init__(self, time_out=60, my_log=None):
        """
        初始化
        :param window_name: 窗口的 Name
        :param window_classname: 窗口的 ClassName
        AutomationId: mainpage
        """
        self.dir_path, _ = os.path.split(sys.argv[0])
        if my_log is None:
            self.log_path = os.path.join(self.dir_path, "result", "log", "CMoveRandomItem.log")
            if not os.path.exists(os.path.split(self.log_path)[0]):
                os.makedirs(os.path.split(self.log_path)[0])
            self.log_path = os.path.join(self.dir_path, "result", "log", "CMoveRandomItem.log")
            self.my_log = MyLogPrint(self.log_path)
        else:
            self.my_log = my_log

        super(CMoveRandomItem, self).__init__(time_out=time_out, my_log=self.my_log)

    def run_logic(self):
        """
        运行控制逻辑
        :return:
        """
        # 点击素材类型
        media_group_control, player_control, info_control = self.get_media_group_control()
        # 获取时间线控件
        time_line_group_control = self.get_time_line_main_product()
        if media_group_control is None:
            self.my_log.print_info("未找到素材类型")
            return False
        name_list = ["Media", "Audio", "Text", "Transition", "Stickers", "Effects", "Filters"]
        if not self.click_media_button(media_group_control, click_name="Media"):
            self.my_log.print_info("点击素材类型失败")
            return False

        # 获取所有的轨道
        all_track_list = self.get_all_track_list(time_line_group_control)

        # 获取时间刻度控件  第一个为时间刻度指针 第二个为时间刻度控件
        pointer_control, time_line_control = self.get_time_line_pointer(time_line_group_control)
        width, height = self.Get_control_size(time_line_control)
        left2, top2, right2, bottom2 = self.Get_control_local(time_line_control)

        while True:
            track_index = random.randint(0, len(all_track_list) - 1)
            one_track = all_track_list[track_index]
            self.set_one_track_visible(time_line_group_control, one_track)

            left, top, right, bottom = self.Get_control_local(pointer_control)
            height = bottom - top
            x = random(0, width)
            time_line_control.Click(x, height/2)

            left1, top1, right1, bottom1 = self.Get_control_local(pointer_control)

            if left1 == left:
                width = left1 - left2

    def radom_move_items(self):
        """
        随机移动控件
        :return:
        """
        pic_path = os.path.join(self.dir_path, "temp", "pic")
        if not os.path.exists(pic_path):
            os.makedirs(pic_path)
        # 点击素材类型
        # media_group_control, player_control, info_control = self.get_media_group_control()
        # 获取时间线控件
        time_line_group_control = self.get_time_line_main_product()

        # 获取所有的轨道
        all_track_list = self.get_all_track_list(time_line_group_control)

        # 获取时间刻度控件  第一个为时间刻度指针 第二个为时间刻度控件
        pointer_control, time_line_control = self.get_time_line_pointer(time_line_group_control)
        width, height = self.Get_control_size(time_line_control)
        left2, top2, right2, bottom2 = self.Get_control_local(time_line_control)

        # 时间轨道父节点
        track_parent = self.get_track_parent(time_line_group_control)
        left_track_parent, top_track_parent, right_track_parent, bottom_track_parent = self.Get_control_local(track_parent)
        width_track_parent = right_track_parent - left_track_parent
        height_track_parent = bottom_track_parent - top_track_parent

        # self.get_track_zoom_ratio(time_line_group_control)

        # self.time_line_orthogonal_scroll_bar_move(time_line_group_control, random.randint(20, 80))

        move_number = 50
        while move_number > 0:
            try:
                track_index = random.randint(0, len(all_track_list) - 1)
                one_track = all_track_list[track_index]
                self.my_log.print_info("track_index:", track_index)
                self.set_one_track_visible(time_line_group_control, one_track)
                # one_track.Click()

                left_one_track, top_one_track, right_one_track, bottom_one_track = self.Get_control_local(one_track)
                width_one_track = right_one_track - left_one_track
                height_one_track = bottom_one_track - top_one_track

                # 轨道截图
                pic_name = time.strftime("%Y%m%d%H%M%S", time.localtime()) + "_{0}.png".format(track_index)
                pic_name = os.path.join(pic_path, pic_name)
                self.my_log.print_info((left_one_track, top_one_track, width_one_track, height_one_track))
                self.get_app_screen_2(pic_name, reg=(left_one_track, top_one_track),
                                      size=(width_one_track, height_one_track), handle=1)

                # 获取轨道上的项的位置
                all_item = self.get_track_item_local(pic_name)
                if len(all_item) == 0:
                    self.my_log.print_info("未找到轨道项", pic_name)
                    continue
                self.my_log.print_info(all_item)
                try:
                    item_index = random.randint(0, len(all_item) - 1)
                except:
                    item_index = 0
                try:
                    x1 = left_one_track + random.randint(all_item[item_index]["start"], all_item[item_index]["end"])
                except:
                    self.my_log.print_info("item_index: {0}".format(item_index), len(all_item))
                    self.my_log.print_info(traceback.format_exc())
                    continue
                y1 = top_one_track + random.randint(1, height_one_track-1)

                x2 = left_track_parent + random.randint(100,  random.randint(1, width_track_parent))
                y2 = top_track_parent + random.randint(50, random.randint(1, height_track_parent))

                self.my_log.print_info("x1: {0}, y1: {1}, x2: {2}, y2: {3}".format(x1, y1, x2, y2))
                self.drag_drop_mouse(x1, y1, x2, y2)

                if random.randint(0, 10) == 5:
                    # 改变缩放比列
                    self.get_track_zoom_ratio(time_line_group_control, random.randint(30, 80))

                if random.randint(0,10) == 5:
                    # 拖动后重新 获取所有的轨道
                    self.time_line_orthogonal_scroll_bar_move(time_line_group_control, random.randint(20, 80))

                # 拖动后重新 获取所有的轨道
                all_track_list = self.get_all_track_list(time_line_group_control)

            except:
                self.my_log.print_info(traceback.format_exc())

            move_number -= 1

        self.main_product.SetTopmost(False)


if __name__ == '__main__':
    test = CMoveRandomItem()
    test.radom_move_items()
