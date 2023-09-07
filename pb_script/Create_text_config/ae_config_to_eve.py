# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:ae_config_to_eve.py
@className:
@Create Data:2023/8/22 14:22 14:08
@Description:
把ae工程转换为eve配置文件
"""

import os
import time
import sys
import traceback
import json5
from collections import OrderedDict
from copy import deepcopy
import re


def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json5.load(f)


def write_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json5.dump(data, f)


def update_pos(one_layer, all_layers):
    """
    递归更新布局中位置信息
    :param one_layer:
    :param all_layers:
    :return:
    """
    if one_layer["parent"] == "":
        temp_pos = [
            one_layer["pos"][0] - one_layer["anchor_point"][0],
            one_layer["pos"][1] - one_layer["anchor_point"][1],
            one_layer["pos"][2] - one_layer["anchor_point"][2],
        ]
        return temp_pos
    else:
        parent_id = one_layer["parent"]
        for layer in all_layers:
            if layer["ind"] == parent_id:
                temp_pos = update_pos(layer, all_layers)
                print("-----1", temp_pos)
                temp_pos1 = [
                    int(one_layer["pos"][0] - one_layer["anchor_point"][0] + temp_pos[0]),
                    int(one_layer["pos"][1] - one_layer["anchor_point"][1] + temp_pos[1]),
                    int(one_layer["pos"][2] - one_layer["anchor_point"][2] + temp_pos[2]),
                ]
                return temp_pos1


def run_logic():
    """

    :return:
    """
    # 读取源文件数据
    source_file_path = r"E:\MyProject\PythonProject\pythonProject\EVE\pb_script\Create_text_config\OOPS (converted)\OOPS (converted)1.json"
    source_data = read_json(source_file_path)

    # 读取模板文件中的json数据
    template_file_path = r"E:\MyProject\PythonProject\pythonProject\EVE\pb_script\Create_text_config\template_json\Template_pb.json"
    template_data = read_json(template_file_path)

    # 拷贝一份模板文件到目标目录
    target_file_path = r"E:\MyProject\PythonProject\pythonProject\EVE\pb_script\Create_text_config\OOPS (converted)\OOPS (converted)1_eve.json"

    # 提取json文件中的数据
    # 获取工程配置信息
    template_data["project_name"] = source_data["nm"]
    template_data["fr"] = source_data["fr"]
    template_data["op"] = source_data["op"]
    template_data["w"] = source_data["w"]
    template_data["h"] = source_data["h"]
    template_data["project_duration"] = (source_data["op"]/source_data["fr"])*1000

    layers = []

    for one_layer in source_data["layers"]:
        ere_one_layer = template_data["layers"][0]
        ere_one_layer["ind"] = one_layer["ind"]
        if "parent" in one_layer.keys():
            ere_one_layer["parent"] = one_layer["parent"]
        else:
            ere_one_layer["parent"] = ""
        ere_one_layer["nm"] = one_layer["nm"]
        if "t" in one_layer.keys():
            ere_one_layer["type"] = "text"
            ere_one_layer["image_path"] = ""
        else:
            ere_one_layer["type"] = "image"
            ere_one_layer["image_path"] = "file path"

        # 计算位置信息 在ae中位置信息是通过锚点 ks-a 和ks-p两个点位置结合算出来的  还需要更具父目录的层级去计算位置
        ere_one_layer["pos"] = [
            one_layer["ks"]["p"]["k"][0],
            one_layer["ks"]["p"]["k"][1],
            one_layer["ks"]["p"]["k"][2],
        ]
        # 计算缩放信息
        ere_one_layer["resizing"] = []
        source_resizing = one_layer["ks"]["s"]["k"]
        if isinstance(source_resizing[0], dict):
            for item in source_resizing:
                temp_dic = OrderedDict([("time", 0), ("value", [])])
                temp_dic["time"] = item["t"] * (1000/source_data["fr"])
                temp_dic["value"] = item["s"]

                ere_one_layer["resizing"].append(deepcopy(temp_dic))
        elif isinstance(source_resizing[0], list):
            ere_one_layer["resizing"] = [
                OrderedDict([("time", 0), ("value", source_resizing)]),
                OrderedDict([("time", template_data["project_duration"]), ("value", source_resizing)]),
            ]
        # 计算锚点信息
        ere_one_layer["anchor_point"] = one_layer["ks"]["a"]["k"]

        # 计算旋转信息 旋转中心点
        rotation_data = one_layer["ks"]["r"]["k"]
        ere_one_layer["rotation"]["axis_of_rotation"] = "z"
        if isinstance(rotation_data, int):  # 0表示没有旋转
            ere_one_layer["rotation"]["rotation_point"] = [
                    one_layer["ks"]["p"]["k"][0],
                    one_layer["ks"]["p"]["k"][1],
                    one_layer["ks"]["p"]["k"][2],
            ]
            ere_one_layer["rotation"]["rotation_value"] = [
                OrderedDict([("time", 0), ("value", rotation_data)]),
                OrderedDict([("time", template_data["project_duration"]), ("value", rotation_data)])
            ]
        else:
            ere_one_layer["rotation"]["rotation_point"] = [
                    one_layer["ks"]["p"]["k"][0],
                    one_layer["ks"]["p"]["k"][1],
                    one_layer["ks"]["p"]["k"][2],
            ]
            ere_one_layer["rotation"]["rotation_value"] = []
            for item in rotation_data:
                temp_dic = OrderedDict([("time", 0), ("value", [])])
                temp_dic["time"] = item["t"] * (1000 / source_data["fr"])
                temp_dic["value"] = item["s"]

                ere_one_layer["rotation"]["rotation_value"].append(deepcopy(temp_dic))

        # 计算透明度
        ere_one_layer["opacity"] = one_layer["ks"]["o"]["k"]

        if "t" in one_layer.keys():
            # 获取文字信息
            text_data = one_layer["t"]["d"]["k"][0]["s"]
            print(text_data)
            if "x" in one_layer["t"]["d"]:
                part_name = one_layer["t"]["d"]["x"]
                pattern = re.compile(r"[(](.*?)[)]", re.S)
                s = re.findall(pattern, part_name)
                if len(s) > 0:
                    for one_layer_1 in source_data["layers"]:
                        if one_layer_1["nm"] == s[0].replace("'", ""):
                            ere_one_layer["text"]["default_value"] = one_layer_1["t"]["d"]["k"][0]["s"]["t"]
                else:
                    ere_one_layer["text"]["default_value"] = ""
            else:
                ere_one_layer["text"]["default_value"] = text_data["t"]
            ere_one_layer["text"]["text_size"] = text_data["s"]
            ere_one_layer["text"]["fonts_name"] = text_data["f"]
            ere_one_layer["text"]["fonts_alignment"] = text_data["j"]
            ere_one_layer["text"]["fonts_color"] = [int(i*256) for i in text_data.get("fc", [])]
            ere_one_layer["text"]["stroke_color"] = [int(i*256) for i in text_data.get("sc", [])]
            ere_one_layer["text"]["stroke_w"] = text_data.get("sw", [])
            ere_one_layer["text"]["line_h"] = text_data["lh"]

        layers.append(deepcopy(ere_one_layer))

    print(layers)

    # 重新计算位置信息
    new_layers = []
    for layer in layers:
        # 计算位置信息 在ae中位置信息是通过锚点 ks-a 和ks-p两个点位置结合算出来的  还需要更具父目录的层级去计算位置
        temp_pos1 = update_pos(layer, layers)

        temp_layer = deepcopy(layer)
        temp_layer["pos"] = temp_pos1

        # 重新计算旋转点 旋转点为 位置+ 锚点的值
        temp_layer["rotation"]["rotation_point"] = [
            int(temp_layer["pos"][0] + temp_layer["anchor_point"][0]),
            int(temp_layer["pos"][1] + temp_layer["anchor_point"][1]),
            int(temp_layer["pos"][2] + temp_layer["anchor_point"][2]),
        ]

        new_layers.append(deepcopy(temp_layer))
        print("-----2", layer["pos"])


    # 获取模板文件
    template_data["layers"] = new_layers
    # 写入数据
    write_json(target_file_path, template_data)


if __name__ == '__main__':
    run_logic()

