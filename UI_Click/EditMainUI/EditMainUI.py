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

import pyautogui

from CaseRealization.Public.clipboard import Send_ctrl_v, Send_ctrl_a, Send_enter

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

        self.ui_big = self.get_ui_big()

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
        # self.my_log.print_info(child_all)
        custom_control = None
        for item in child_all:
            if item.Name == "" and item.ControlTypeName == "CustomControl" and item.ClassName == "QSplitter":
                custom_control = item
        if custom_control is None:
            return None, None, None

        child_all = custom_control.GetChildren()

        media_group_control = None
        for item in child_all:
            if item.Name == "" and item.ControlTypeName == "CustomControl" and item.ClassName == "QSplitter":
                media_group_control = item

        if media_group_control is None:
            return None, None, None

        child_all = media_group_control.GetChildren()

        media_group_control = child_all[2]
        player_control = child_all[1]
        info_control = child_all[0]

        if media_group_control.ControlTypeName == player_control.ControlTypeName == info_control.ControlTypeName:
            return media_group_control, player_control, info_control
        return None, None, None

    def click_media_button(self, media_group_control=None, click_name="Media") -> bool:
        """
        根据传入的值类型
        :param media_group_control:
        :param click_name:
        :return:
        """
        if media_group_control is None:
            # 点击素材类型
            media_group_control, player_control, info_control = self.get_media_group_control()
            if media_group_control is None:
                self.my_log.print_info("未找到素材类型")
                return False
        try:
            # print(media_group_control.GetChildren())
            all_check_box = media_group_control.GetChildren()[0].GetChildren()
            for item in all_check_box:
                # self.my_log.print_info(item.Name, item.Name == click_name)
                if item.Name == click_name:
                    item.Click()
                    return True
            return False
        except:
            self.my_log.print_info(media_group_control.GetChildren())
            self.my_log.print_info(traceback.format_exc())
            return False

    def get_media_info_items(self, media_group_control=None) -> list[uiautomation.Control]:
        """
        获取所有list 控件
        :param media_group_control:
        :return:
        """
        if media_group_control is None:
            # 获取素材类型
            media_group_control, player_control, info_control = self.get_media_group_control()
            if media_group_control is None:
                self.my_log.print_info("未找到素材类型")
                return False
        all_list_control = []
        child_all = self.Get_all_child(media_group_control)
        for item in child_all:
            try:
                if item.ClassName == "QListView" and item.ControlTypeName == "ListControl":
                    all_list_control.append(item)
            except:
                pass

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

    def get_track_zoom_ratio(self, time_line_main_product=None, set_value=-1, click_type="drag_drop"):
        """
        获取轨道缩放比例
        :return:
        """
        set_value = int(set_value)
        if time_line_main_product is None:
            time_line_main_product = self.get_time_line_main_product()

        all_funiction_control = time_line_main_product.GetChildren()[-1]

        slider_control = all_funiction_control.GetChildren()[-2]

        present_value = int(slider_control.GetValuePattern().Value)
        # print(slider_control.GetRangeValuePattern().Value, slider_control.GetSelectionPattern(), slider_control.GetValuePattern().Value)

        self.my_log.print_info("get_track_zoom_ratio  get_track_zoom_ratio:", present_value)

        if set_value < 0:
            return present_value
        if click_type == "drag_drop":
            drag_drop_control = all_funiction_control.GetChildren()[-2]
            left, top, right, bottom = self.Get_control_local(drag_drop_control)
            width = right - left
            height = bottom - top

            drag_drop_control.Click(int(width/100 * set_value), int(height/2))
            present_value = int(slider_control.GetValuePattern().Value)

            self.my_log.print_info("set set_value:", present_value)
            if present_value != set_value:
                return False
            return True

        up_button = all_funiction_control.GetChildren()[-1]
        down_button = all_funiction_control.GetChildren()[-3]
        click_times = 1
        if present_value < set_value:
            while present_value < set_value:
                up_button.Click()
                present_value = int(slider_control.GetValuePattern().Value)
                click_times += 1
                if click_times > 50:
                    return False
            self.my_log.print_info("set set_value:", present_value)
            return True
        click_times = 1
        while present_value > set_value:
            down_button.Click()
            present_value = int(slider_control.GetValuePattern().Value)
            click_times += 1
            if click_times > 50:
                return False
        self.my_log.print_info("set set_value:", present_value)
        return True

    def add_local_file(self, add_button_control, file_path: str, file_name_string: str = None) -> bool:
        """
        添加本地文件
        :param file_path:
        :return:
        """
        add_button_control.Click()
        time.sleep(2)

        choose_folder = self.main_product.GetChildren()[0]

        if choose_folder.Name != "Choose folder or files":
            self.my_log.print_info("添加文件失败")
            return False

        all_child = choose_folder.GetChildren()

        ok_button = all_child[-5]
        choose_folder_button = all_child[-6]
        file_name_input = all_child[2]
        file_items = all_child[0]
        input_path = all_child[-2]

        input_path_control = None
        # 寻找输入地址的地址栏控件位置
        for item in self.Get_all_child(input_path):
            if item.ClassName == "ToolbarWindow32" and item.ControlTypeName == "ToolBarControl" and ": " in item.Name:
                input_path_control = item
                break
        if input_path_control is None:
            self.my_log.print_info("添加文件失败")
            return False
        left, top, right, bottom = self.Get_control_local(input_path_control)
        width = right - left
        height = bottom - top

        # 点击文件输入的尾部
        self.my_log.print_info("click input_path_control:", width - 10 * self.ui_big, height/2)
        input_path_control.Click(width - 10 * self.ui_big, int(height/2))
        time.sleep(0.5)
        # 发送control v
        Send_ctrl_v(file_path)
        time.sleep(0.5)
        Send_enter()
        time.sleep(0.5)

        # 是否选择指定的文件
        if file_name_string is not None:
            file_name_input.Click()
            time.sleep(0.5)
            Send_ctrl_v(file_name_string)
            time.sleep(0.5)
        else:
            # 点击文件列表
            choose_folder.Click()
            time.sleep(0.5)
            # 发送control a全选
            Send_ctrl_a()
            time.sleep(0.5)

        # 点击添加按钮
        ok_button.Click()
        time.sleep(2)

    def set_app_max(self):
        """
        设置窗口最大化
        :return:
        """
        width, height = self.Get_control_size(self.main_product)
        w, h = pyautogui.size()

        # 如果界面宽度小于屏幕宽度减100 则点击最大化按钮
        if width > w - 100:
            return True

        all_children = self.main_product.GetChildren()

        max_button = all_children[3]

        max_button.Click()

        width1, height1 = self.Get_control_size(self.main_product)

        if width1 >= width:
            return True
        max_button.Click()

        return True

    def set_media_item_visible(self, media_item, media_group_control):
        """
        将meida中的某一个选项调整为界面显示可见
        :param media_item:
        :param media_group_control:
        :return:
        """
        media_group_control_1 = media_group_control.GetChildren()[-1]
        left, top, right, bottom = self.Get_control_local(media_group_control_1)
        left_item, top_item, right_item, bottom_item = self.Get_control_local(media_item)

        scroll_time = 1
        while top_item < top:
            self.scroll_bar_move(value=100, direction=1)
            left_item, top_item, right_item, bottom_item = self.Get_control_local(media_item)
            if scroll_time > 20:
                return False
            scroll_time += 1

        scroll_time = 1
        while bottom_item > bottom:
            self.scroll_bar_move(value=100, direction=-1)
            left_item, top_item, right_item, bottom_item = self.Get_control_local(media_item)
            if scroll_time > 20:
                return False
            scroll_time += 1

        return True

    def select_media_add_to_track(self, media_group_control=None, list_index=0, item_index=1, item_name="Text",
                                  track_index=0, track_local=0.5):
        """
        选择文件列表中的某一个列表下的某一个文件 拖动到时间线上 优先使用item_index 如果item_index==-1则使用item_name
        :param media_group_control: 列表控件，如果没有则重新寻找
        :param list_index: 类别index
        :param item_index: 具体某一项的index
        :param item_name: 某一项的名称
        :param track_index: 轨道index
        :param track_local: 轨道位置 比列（轨道的宽乘以这个比列）
        :return:
        """
        list_index = int(list_index)
        item_index = int(item_index)
        track_local = float(track_local)
        track_index = int(track_index)
        if media_group_control is None:
            # 点击素材类型
            media_group_control, player_control, info_control = self.get_media_group_control()
            if media_group_control is None:
                self.my_log.print_info("未找到素材类型")
                return False

        # 获取该素材下的所有子元素
        all_list_control = self.get_media_info_items(media_group_control)

        # 随机选择一个列表
        all_items = all_list_control[list_index].GetChildren()
        self.my_log.print_info("总共有{0}个分类  第{1}分类中元素个数为:{2}".format(len(all_items), list_index,
                                                                                   len(all_list_control)))

        items = all_items[item_index]

        # 将item显示出来
        self.set_media_item_visible(items, media_group_control)
        items.Click()

        # 获取所有的轨道
        time_line_group_control = self.get_time_line_main_product()
        all_track = self.get_all_track_list(time_line_group_control)

        # 列表中第一个轨道便是主轨（如果没有先添加主轨则该处逻辑不正确）
        main_track = all_track[track_index]

        # 设置轨道可见
        self.set_one_track_visible(time_line_group_control, main_track)

        left_items, top_items, right_items, bottom_items = self.Get_control_local(items)
        left_main_track, top_main_track, right_main_track, bottom_main_track = self.Get_control_local(main_track)

        x1 = left_items + int((right_items - left_items) / 2)
        y1 = top_items + int((bottom_items - top_items) / 2)

        # 将素材拖动至轨道中间下
        x2 = left_main_track + int((right_main_track - left_main_track) * track_local)
        y2 = bottom_main_track - 10
        self.my_log.print_info("x1:{0} y1:{1} x2:{2} y2:{3}".format(x1, y1, x2, y2))
        self.drag_drop_mouse(x1, y1, x2, y2, 2)

        return True

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
            item_group = media_group_control.GetChildren()[1].GetChildren()[0]
            all_child = self.Get_all_child(item_group)
            add_button = None
            for item in all_child:
                try:
                    if item.ClassName == "QPushButton":
                        add_button = item
                        break
                except:
                    # self.my_log.print_info(traceback.format_exc())
                    pass
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
            self.my_log.print_info("添加失败", type)
            return False
        print(self.main_product)
        return True



