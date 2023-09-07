# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:jianyin_to_eve.py
@className:
@Create Data:2023/9/1 9:59 14:08
@Description:
将剪映工程转换为eve工程
"""
import os
import json
import time
import sys
import traceback
import re
from copy import deepcopy
from collections import OrderedDict
import shutil

from CaseRealization.Public.file_zip import CFile_zip


text_track_item_templates = {
                    "left": 263333.3333333333,
                    "material": "{00000000-0000-0000-0000-000000000000}",
                    "originalDuration": 0,
                    "right": 268333.3333333333,
                    "texts": [{
                            "id": "{00000000-0000-0000-0000-000000000000}",
                            "text": "Text Here"
                        }
                    ],
                    "type": 3,
                    "volume": 1
                }

sticker_track_item_templates = {
                    "height": 1,
                    "left": 205166.66666666666,
                    "material": "{22586423-4569-320e-66e3-b4b702000000}",
                    "originalDuration": 0,
                    "right": 273333.3333333333,
                    "type": 5,
                    "volume": 1,
                    "width": 1
                }

effect_track_item_templates = {
                    "height": 1,
                    "left": 238700,
                    "material": "{bf498a19-53a8-447e-b0bf-48817d2e7348}",
                    "originalDuration": 0,
                    "right": 291500,
                    "type": 6,
                    "volume": 1,
                    "width": 1
                }

filter_track_item_templates = {
                    "height": 1,
                    "left": 248933.33333333334,
                    "material": "{80570c7f-8824-42d1-8400-bc0dbbcbef2d}",
                    "originalDuration": 0,
                    "right": 304266.6666666667,
                    "type": 7,
                    "volume": 1,
                    "width": 1
                }

video_track_item_templates = {
                    "height": 1080,
                    "left": 0,
                    "material": "{ceaf302c-2e62-466e-938e-2a745fa87111}",
                    "originalDuration": 299515,
                    "path": "E:/Music/MV/胡彦斌-刘柏辛Lexie-天赐的声音-新世界 (《天赐的声音 第四季》 第1期)(蓝光).mp4",
                    "right": 299515,
                    "rightTransitionDuration": 2000,
                    "rightTransitionId": "{a9293845-8ea7-4b02-a1f3-ba86ff38e4f7}",
                    "type": 1,
                    "volume": 1,
                    "width": 1920
                }

audio_track_item_templates = {
                    "height": 1,
                    "left": 42733.333333333336,
                    "material": "{b9349785-ef38-412c-b488-69e0979dce73}",
                    "originalDuration": 222656,
                    "path": "C:/Users/31447/OneDrive/音乐/MV/刘惜君-王赫野-大风吹 (天赐的声音第二季 第12期)(超清).mp4",
                    "right": 265389.3333333333,
                    "type": 2,
                    "volume": 1,
                    "width": 1
                }

track_templates  = {
            "hide": False,
            "items": [],
            "lock": False,
            "mute": False,
            "type": 7
        }

def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def update_project_json(jianying_data, eve_project_path):
    """
    {
        "canvasHeight": 1080, 工程高
        "canvasWidth": 1920, 工程宽
        "cover": false,
        "duration": 599020, 工程时长
        "frameRateDen": 1,
        "frameRateNum": 30, 工程帧率
        "freeLayer": false, 工程是否开启自由层级
        "ratioDen": 9, 工程比列 宽
        "ratioNum": 16,工程比列 高
        "version": 256
    }
    :return:
    """
    eve_project_json_path = os.path.join(eve_project_path, "project.json")
    # 读取json数据
    eve_project = read_json(eve_project_json_path)
    if not os.path.exists(eve_project_json_path):
        print("eve工程配置json文件不存在:", eve_project_json_path)
    # 修改项目参数
    eve_project["canvasHeight"] = int(jianying_data["canvas_config"]["height"])
    eve_project["canvasWidth"] = int(jianying_data["canvas_config"]["width"])
    if jianying_data["canvas_config"]["ratio"] in ["original", "custom"]:
        eve_project["ratioDen"] = 9
        eve_project["ratioNum"] = 16
    else:
        eve_project["ratioDen"] = int(jianying_data["canvas_config"]["ratio"].split(":")[0])
        eve_project["ratioNum"] = int(jianying_data["canvas_config"]["ratio"].split(":")[1])
    eve_project["duration"] = int(jianying_data["duration"]/1000)
    eve_project["frameRateNum"] = int(jianying_data["fps"])
    # 写文件
    write_json(eve_project_json_path, eve_project)


def update_path(jianying_project_path, eve_project_path, items, item_info, dir_type="media"):
    """
    更新剪映中的路劲信息
    :param jianying_project_path:
    :param items:
    :return:
    """
    media_temp_json = os.path.join(dir_pat, "template", "media", "material.json")
    media_temp_json_data = read_json(media_temp_json)

    path = items["path"]
    material = items["material"]
    new_path = os.path.join(eve_project_path, dir_type, material)
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    if not os.path.exists(path):
        if "##_draftpath" in path:
            temp_path = jianying_project_path
            for item in path.split(r"/"):
                if "##_draftpath" in item:
                    continue

                temp_path = os.path.join(temp_path, item)
            media_temp_json_data["fileName"] = temp_path
    else:
        media_temp_json_data["fileName"] = path

    if item_info["type"] != "photo":
        media_temp_json_data["materialAudioInfo"]["duration"] = item_info["duration"]
        media_temp_json_data["materialBasicInfo"]["duration"] = item_info["duration"]
        media_temp_json_data["materialVideoInfo"]["duration"] = item_info["duration"]
        media_temp_json_data["materialVideoInfo"]["height"] = item_info["height"]
        media_temp_json_data["materialVideoInfo"]["width"] = item_info["width"]
    else:
        media_temp_json_data["materialBasicInfo"]["duration"] = 40
        media_temp_json_data["materialVideoInfo"]["duration"] = 40

        media_temp_json_data["materialVideoInfo"]["height"] = item_info["height"]
        media_temp_json_data["materialVideoInfo"]["width"] = item_info["width"]

    items["path"] = media_temp_json_data["fileName"]
    print("path-------------", items["path"])
    media_json_path = os.path.join(new_path, "material.json")
    write_json(media_json_path, media_temp_json_data)



def update_track(jianying_data, eve_project_path, jianying_project_path):
    """
    更新轨道布局信息
    {
            "hide": false,
            "items": [
                {
                    "height": 1,
                    "left": 248933.33333333334,
                    "material": "{80570c7f-8824-42d1-8400-bc0dbbcbef2d}",
                    "originalDuration": 0,
                    "right": 304266.6666666667,
                    "type": 7,
                    "volume": 1,
                    "width": 1
                }
            ],
            "lock": false,
            "mute": false,
            "type": 7
        }
    :param jianying_data:
    :param eve_project_path:
    :return:
    """

    # 获取所有的媒体信息
    all_materials = jianying_data["materials"]

    all_materials_stickers = OrderedDict()
    for item in all_materials["stickers"]:
        all_materials_stickers[item["id"]] = item

    all_materials_texts = OrderedDict()
    for item in all_materials["texts"]:
        # print(item["id"])
        all_materials_texts[item["id"]] = item

    all_materials_videos = OrderedDict()
    for item in all_materials["videos"]:
        all_materials_videos[item["id"]] = item

    all_materials_audios = OrderedDict()
    for item in all_materials["audios"]:
        all_materials_audios[item["id"]] = item

    # 获取剪映工程中的轨道信息，分成三类
    all_track = jianying_data["tracks"]
    video_track = []
    audio_track = []
    text_track = []
    for one_track in all_track:
        if one_track["type"] == "video":
            video_track.append(one_track)
        elif one_track["type"] == "audio":
            audio_track.append(one_track)
        else:
            text_track.append(one_track)

    # 将轨道添加到EVE工程轨道上 轨道布局为 先文本  后视频  音频
    eve_track_json_path = os.path.join(eve_project_path, "track.json")
    eve_track_json_data = read_json(eve_track_json_path)

    eve_tracks = []
    # 更新文本轨道信息
    ere_text_track = []
    for one_text_track in text_track:
        text_track_template = deepcopy(track_templates)
        # print(one_text_track["type"])
        # 更新轨道类型
        if one_text_track["type"].strip() == "sticker":
            text_track_template["type"] = 5
            temp_item = deepcopy(sticker_track_item_templates)
        elif one_text_track["type"].strip() == "text":
            text_track_template["type"] = 4
            temp_item = deepcopy(text_track_item_templates)
        elif "effect" in one_text_track["type"].strip():
            text_track_template["type"] = 6
            temp_item = deepcopy(effect_track_item_templates)
        elif "filter" in one_text_track["type"].strip():
            text_track_template["type"] = 7
            temp_item = deepcopy(filter_track_item_templates)
        else:
            print("type not support:", one_text_track["type"])
            text_track_template["type"] = 4
            temp_item = deepcopy(text_track_item_templates)

        # print("temp_item-------------", temp_item)
        # 更新轨道中的项
        track_items = []
        for item in one_text_track["segments"]:
            # 修改位置信息
            temp_item["left"] = item["target_timerange"]["start"]/1000
            temp_item["right"] = temp_item["left"] + item["target_timerange"]["duration"]/1000
            if one_text_track["type"] == "text":
                try:
                    # 获取文本信息
                    text = all_materials_texts[item["material_id"]]["content"]
                    text = re.findall(r">\[(.*?)]<", text)
                    temp_item["texts"][0]["text"] = "".join(text)
                except:
                    temp_item["texts"][0]["text"] = "未获取到文本内容"
                    print("the key id:", item["material_id"])
                    print(traceback.format_exc())
                # print("text-------------", temp_item["texts"][0]["text"])
            elif one_text_track["type"] == "adjust":
                temp_item["texts"][0]["text"] = "不支持的轨道格式adjust"
            # print("temp_item-------------", temp_item["left"], temp_item["right"])
            track_items.append(temp_item)

        text_track_template["items"] = track_items
        ere_text_track.insert(0, text_track_template)

    # 跟新视频轨道信息
    ere_video_track = []
    for one_video_track in video_track:
        video_track_template = deepcopy(track_templates)
        video_track_template["type"] = 2
        # 更新轨道中的项
        track_items = []
        for item in one_video_track["segments"]:
            temp_item = deepcopy(video_track_item_templates)
            video_info = all_materials_videos[item["material_id"]]
            # 宽高
            temp_item["height"] = video_info["height"]
            temp_item["width"] = video_info["width"]
            # 位置
            temp_item["left"] = item["target_timerange"]["start"] / 1000
            temp_item["right"] = temp_item["left"] + item["target_timerange"]["duration"]/1000
            # id
            temp_item["material"] = "{00000000-0000-0000-0000-00" + str(time.time())[:10] + "}"
            temp_item["originalDuration"] = item["source_timerange"]["duration"]/1000
            temp_item["rightTransitionDuration"] = 0
            temp_item["rightTransitionId"] = ""
            temp_item["path"] = video_info["path"]
            time.sleep(1)  # 防止时间重复
            update_path(jianying_project_path, eve_project_path, temp_item, video_info)
            track_items.insert(0, temp_item)

        video_track_template["items"] = track_items
        ere_video_track.insert(0, video_track_template)
    ere_video_track[-1]["type"] = 1

    # 跟新音频轨道
    ere_audio_track = []
    for one_audio_track in audio_track:
        audio_track_template = deepcopy(track_templates)
        audio_track_template["type"] = 3
        track_items = []
        for item in one_audio_track["segments"]:
            temp_item = deepcopy(audio_track_item_templates)
            audio_info = all_materials_audios[item["material_id"]]
            temp_item["left"] = item["target_timerange"]["start"]/1000
            temp_item["right"] = temp_item["left"] + item["target_timerange"]["duration"]/1000
            temp_item["material"] = "{00000000-0000-0000-0000-00" + str(time.time())[:10] + "}"
            temp_item["originalDuration"] = item["source_timerange"]["duration"]/1000
            temp_item["path"] = audio_info["path"]
            time.sleep(1)  # 防止时间重复
            update_path(jianying_project_path, eve_project_path, temp_item, video_info)
            track_items.insert(0, temp_item)
        audio_track_template["items"] = track_items
        ere_audio_track.insert(0, audio_track_template)

    eve_tracks = ere_text_track + ere_video_track + ere_audio_track
    eve_track_json_data["tracks"] = eve_tracks

    write_json(eve_track_json_path, eve_track_json_data)


def run_logic(template_dir, save_dir, jianying_project_path):
    """
    运行逻辑
    :return:
    """
    # 判断剪映配置文件是否存在
    draft_content_json = os.path.join(jianying_project_path, "draft_content.json")
    if not os.path.exists(draft_content_json):
        print("文件不存在", draft_content_json)
        return
    # 获取最后一层的文件夹名称为工程名称 并在eve目录下创建新的文件夹
    project_name = os.path.split(jianying_project_path)[-1]

    # new_dir = os.path.join(save_dir, time.strftime("%Y%m%d%H%M%S", time.localtime(time.time())))
    new_dir = os.path.join(save_dir, project_name)
    if os.path.exists(new_dir):
        shutil.rmtree(new_dir)
    # 新工程的名称和完整路劲
    save_dir = new_dir + ".zip"
    if os.path.exists(save_dir):
        os.remove(save_dir)
    # 拷贝一份模板文件夹并重命名
    shutil.copytree(template_dir, new_dir)
    # 获取剪映工程配置的数据
    jianying_data = read_json(draft_content_json)
    # 更新eve工程配置
    update_project_json(jianying_data, new_dir)
    # 跟新eve轨道信息和布局
    update_track(jianying_data, new_dir, jianying_project_path)

    my_zip = CFile_zip()
    save_dir = new_dir + ".zip"
    if os.path.exists(save_dir):
        os.remove(save_dir)
    my_zip.File_zip(new_dir, save_dir)


if __name__ == '__main__':
    dir_pat, _ = os.path.split(sys.argv[0])

    template_dir = r"C:\Users\31447\AppData\Roaming\EaseUS\Video Editor\Projects\20233801153812"
    save_dir = r"C:\Users\31447\AppData\Roaming\EaseUS\Video Editor\Projects"
    jianying_project_save_dir = r"E:\剪影工程模板-capcut\2022年7月27日更新-共15套【源文件】"

    pirject_file_dir_list = []
    for root, dirs, files in os.walk(jianying_project_save_dir):
        for dir in dirs:
            full_path = os.path.join(root, dir)
            json_path = os.path.join(full_path, "draft_content.json")
            if os.path.exists(json_path):
                pirject_file_dir_list.append(full_path)
    print(pirject_file_dir_list)

    # 循环遍历所有符合的文件夹
    # jianying_project_path = r"C:\Users\31447\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\剪映模板001-11秒-横屏-分屏显示个人说话模板"
    for one_dir in pirject_file_dir_list:
        try:
            run_logic(template_dir, save_dir, one_dir)
        except:
            print("convert error:", one_dir)
            print(traceback.format_exc())




