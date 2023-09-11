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

    def click_add_media_item(self, file_path, file_name=None, type="Media"):
        """
        点击添加按钮添加文件
        :param file_path:
        :param file_name:
        :return:
        """
        print(self.main_product)
        first_child = self.main_product.GetChildren()[0]
        # 如果已经存在文件选择弹窗则关闭
        if first_child.Name == "Choose folder or files":
            first_child.GetChildren()[-4].Click()
            time.sleep(0.5)

        # 获取素材类型
        media_group_control, player_control, info_control = self.get_media_group_control()
        if media_group_control is None:
            self.my_log.print_info("未找到素材类型")
            return False

        self.click_media_button(media_group_control, click_name=type)

        if type == "Media":
            # 获取该素材下的所有子元素
            all_list_control = self.get_media_info_items(media_group_control)

            # 第1个是包含添加的控件
            index = 0
            all_items = all_list_control[index].GetChildren()
            # 第一个为添加按钮
            items_index = 0
            self.my_log.print_info("随机拖动第{0}个元素".format(items_index))
            add_button = all_items[items_index]
        else:
            item_group = media_group_control.GetChildren()[1].GetChildren()
            all_child = self.Get_all_child(item_group)
            add_button = None
            for item in all_child:
                if item.GetClassName() == "Button":
                    add_button = item
                    break
        if add_button is None:
            self.my_log.print_info("未找到添加按钮", type)
            return False

        try:
            self.add_local_file(add_button, file_path, file_name)
        except:
            self.my_log.print_info(traceback.format_exc())
            first_child = self.main_product.GetChildren()[0]
            # 如果已经存在文件选择弹窗则关闭
            if first_child.Name == "Choose folder or files":
                first_child.GetChildren()[-4].Click()
                time.sleep(0.5)
            return False
        print(self.main_product)
        return True

    def run_logic(self, item_num=30):
        """
        运行控制逻辑
        :return:
        """
        print(self.main_product)
        self.main_product = self.get_project_main_ui(30)
        print(self.main_product)
        # 关闭 windbug
        # self.kill_app("windbg.exe")
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
        while add_times < item_num:
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
                self.my_log.print_info(traceback.format_exc())
                item = self.get_pid_by_name("windbg.exe")
                if item is not None:
                    self.my_log.print_info("关闭windbug")
                    self.kill_app("windbg.exe")
                item = self.get_pid_by_name("VideoEditorQt.exe")
                if item is None:
                    self.my_log.print_info("程序崩溃")
                else:
                    try:
                        first_child = self.main_product.GetChildren()[0]
                        # 如果已经存在文件选择弹窗则关闭
                        if first_child.Name == "Choose folder or files":
                            first_child.GetChildren()[-4].Click()
                            time.sleep(0.5)
                    except:
                        self.my_log.print_info("未找到文件选择弹窗")
                        self.my_log.print_info(traceback.format_exc())

                # 添加至时间线
            add_times += 1

        self.main_product.SetTopmost(False)

    def test_pb(self):
        pass


if __name__ == '__main__':
    test = CAddRandomItem()
    media_path = r"E:\test"
    # test.click_add_media_item(media_path)
    # test.run_logic(5)
    # test.click_media_button(click_name="Media")
    # test.select_media_add_to_track(list_index=0, item_index=1, track_index=0, track_local=0.2)
    # test.select_media_add_to_track(list_index=0, item_index=2, track_index=0, track_local=0.5)
    # test.select_media_add_to_track(list_index=0, item_index=3, track_index=0, track_local=0.3)
    # test.get_track_zoom_ratio(set_value=53, click_type="drag_drop")
    # test.get_track_zoom_ratio(set_value=47, click_type="drag_drop")
    # test.get_track_zoom_ratio(set_value=20, click_type="drag_drop")
    # test.get_track_zoom_ratio(set_value=10, click_type="drag_drop")
    # test.get_track_zoom_ratio(set_value=80, click_type="drag_drop")
    # test.get_track_zoom_ratio(set_value=95, click_type="drag_drop")
    #
    # test.get_track_zoom_ratio(set_value=53, click_type="button")
    # test.get_track_zoom_ratio(set_value=47, click_type="button")
    # test.get_track_zoom_ratio(set_value=20, click_type="button")
    # test.get_track_zoom_ratio(set_value=10, click_type="button")
    # test.get_track_zoom_ratio(set_value=80, click_type="button")
    # test.get_track_zoom_ratio(set_value=95, click_type="button")

    function_pb = getattr(test, "get_track_zoom_ratio")
    function_pb(set_value=50, click_type="button")

    test.main_product.SetTopmost(False)

