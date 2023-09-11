# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:run_logic.py
@className:
@Create Data:2023/9/8 10:29 14:08
@Description:
随机添加素材和随机拖动素材
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
from UI_Click.ProjectMainUI.ProjectMain import CProjectMain
from CaseRealization.Public.eve_base import CEVEBase
from UI_Click.add_random_items.add_random_item import CAddRandomItem
from UI_Click.add_random_items.move_random_item import CMoveRandomItem
from UI_Click.add_random_items.create_new_project import CCreateNewProject


def run_logic():

    # 创建工程
    create_new_project = CCreateNewProject()
    create_new_project.creat_one_project()

    # 初始化编辑界面
    edit_main = CAddRandomItem()
    # 界面最大化
    edit_main.set_app_max()

    # 添加素材
    media_path = r"E:\test"
    edit_main.click_add_media_item(media_path)
    time.sleep(10)
    # 随机添加素材
    edit_main.run_logic(5)

    move_main = CMoveRandomItem()
    move_main.radom_move_items(5)


if __name__ == '__main__':
    run_logic()
