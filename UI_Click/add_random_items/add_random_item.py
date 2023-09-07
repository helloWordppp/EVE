# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:add_random_item.py
@className:
@Create Data:2023/9/6 11:06 14:08
@Description:

"""
import os
import time
import traceback
import sys
import random
import json

from collections import OrderedDict

from CaseRealization.Public.logging_print import MyLogPrint
from UI_Click.EditMainUI.EditMainUI import CEditMainUI


class CAddRandomItem(CEditMainUI):
    def __init__(self, time_out=60, my_log=None):
        """
        初始化
        :param window_name: 窗口的 Name
        :param window_classname: 窗口的 ClassName
        AutomationId: mainpage
        """
        self.dir_path, _ = os.path.split(sys.argv[0])
        if my_log is None:
            self.log_path = os.path.join(self.dir_path, "result", "log", "CAddRandomItem.log")
            if not os.path.exists(os.path.split(self.log_path)[0]):
                os.makedirs(os.path.split(self.log_path)[0])
            self.log_path = os.path.join(self.dir_path, "result", "log", "CAddRandomItem.log")
            self.my_log = MyLogPrint(self.log_path)
        else:
            self.my_log = my_log

        super(CAddRandomItem, self).__init__(time_out=time_out, my_log=self.my_log)

    def run_logic(self):
        """
        运行控制逻辑
        :return:
        """
        # 关闭windbug
        self.kill_app("windbg.exe")
        # 获取时间线控件
        time_line_group_control = self.get_time_line_main_product()

        # 时间轨道父节点 只有轨道区域
        track_parent = self.get_track_parent(time_line_group_control)

        # 获取素材类型
        media_group_control, player_control, info_control = self.get_media_group_control()
        if media_group_control is None:
            self.my_log.print_info("未找到素材类型")
            return False

        add_times = 0
        while add_times < 10:
            try:
                # 点击对应的分类
                name_list = ["Media", "Audio", "Text", "Transition", "Stickers", "Effects", "Filters"]
                click_name = random.choice(name_list)
                if not self.click_media_button(media_group_control, click_name=click_name):
                    self.my_log.print_info("点击素材类型失败")
                    add_times += 1
                    continue

                # 获取该素材下的所有子元素
                all_list_control = self.get_media_info_items(media_group_control)

                # 随机选择一个列表
                index = 0
                all_items = all_list_control[index].GetChildren()
                self.my_log.print_info("类型{0} 总共有{2}个分类  第{3}个分类中元素个数为:{1}".format(click_name, len(all_items), len(all_list_control), index))

                # 随机选择列表中的某一个
                if click_name == "Text":
                    items_index = 0
                else:
                    items_index = 1
                self.my_log.print_info("随机拖动第{0}个元素".format(items_index))
                items = all_items[items_index]

                # 获取item的位置和大小信息
                left_items, top_items, right_items, bottom_items = self.Get_control_local(items)
                width_items = right_items - left_items
                height_items = bottom_items - top_items

                # 获取时间轴控件的位置和大小
                left_time_line, top_time_line, right_time_line, bottom_time_line = self.Get_control_local(track_parent)
                width_time_line = right_time_line - left_time_line
                height_time_line = bottom_time_line - top_time_line

                # 拖动的起始位置和结束位置
                x1 = left_items + random.randint(1, width_items)
                y1 = top_items + random.randint(1, height_items)
                # 拖动的起始位置和结束位置
                x2 = left_time_line + random.randint(1,  width_time_line)
                y2 = top_time_line + random.randint(1, height_time_line)
                # 拖动
                self.drag_drop_mouse(x1, y1, x2, y2)
            except:
                item = self.get_pid_by_name("windbg.exe")
                if item is not None:
                    self.my_log.print_info("关闭windbug")
                    self.kill_app("windbg.exe")
                item = self.get_pid_by_name("VideoEditorQt.exe")
                if item is None:
                    self.my_log.print_info("程序崩溃")
                self.my_log.print_info(traceback.format_exc())
                # 添加至时间线
            add_times += 1

        self.main_product.SetTopmost(False)


if __name__ == '__main__':
    test = CAddRandomItem()
    test.run_logic()

