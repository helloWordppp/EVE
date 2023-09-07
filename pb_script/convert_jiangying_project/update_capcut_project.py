# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:update_capcut_project.py
@className:
@Create Data:2023/8/16 16:50 14:08
@Description:
修改剪映工程文件中素材地址
"""
import os
import sys
import time
import json
import shutil
import traceback
from collections import OrderedDict

from CaseRealization.Public.file_zip import CFile_zip
from CaseRealization.Ffmpeg_Script.get_video_info import CGetVideoInfo


def get_all_zip(zip_path):
    """
    获取一个目录下的所有zip包 递归
    :param zip_path:
    :return:
    """
    all_zip = []
    for root, dirs, files in os.walk(zip_path):
        for file in files:
            if os.path.splitext(file)[1].upper() == ".ZIP":
                all_zip.append(os.path.join(root, file))
    print(all_zip)
    return all_zip


def copy_source_project(project_name):
    """
    拷贝剪影原始工程文件
    :param project_name:
    :return:
    """
    source_dir = os.path.join(jianying_project_path, project_name)
    if os.path.exists(source_dir):
        shutil.rmtree(source_dir)

    shutil.copytree(jianying_template_path, source_dir)

    draft_agency_config = os.path.join(source_dir, "draft_agency_config.json")
    draft_content = os.path.join(source_dir, "draft_content.json")
    # 删除原始的文件
    if os.path.exists(draft_agency_config):
        os.remove(draft_agency_config)
    # 删除原始的文件
    if os.path.exists(draft_content):
        os.remove(draft_content)

    return source_dir


def update_source_video_name(dir_path):
    """
    中文解压后乱码，因此根据draft_meta_info.json中的文件时长进行视频名称修改
    :param dir_path:
    :return:
    """
    draft_meta_info_s = os.path.join(dir_path, "draft_meta_info.json")
    if not os.path.exists(draft_meta_info_s):
        return False
    # draft_meta_info 文件
    with open(draft_meta_info_s, "r", encoding="utf-8") as file_hand:
        draft_meta_info = json.loads(file_hand.read())
    if len(draft_meta_info["draft_materials"]) == 0:
        return False

    if not os.path.exists(os.path.join(dir_path, "videos")):
        return False
    if not os.path.exists(os.path.join(dir_path, "audios")):
        return False

    all_file = []
    for root, dirs, files in os.walk(os.path.join(dir_path, "videos")):
        for one_file in files:
            all_file.append(os.path.join(root, one_file))
    for root, dirs, files in os.walk(os.path.join(dir_path, "audios")):
        for one_file in files:
            all_file.append(os.path.join(root, one_file))

    video_info = OrderedDict()
    my_get_videoinfo = CGetVideoInfo()
    for one_file in all_file:
        print("--one_file--", one_file)
        json_name = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))
        file_info = my_get_videoinfo.Get_video_info_mediainfo(one_file, json_name)
        print("--file_info--", file_info)
        if len(file_info) == 0:
            continue
        if "Duration" in file_info[0].keys():
            # file_name = os.path.split(one_file)[-1]
            video_info[float(file_info[0]["Duration"]) * 1000] = one_file

    for one_value in draft_meta_info["draft_materials"]:
        for one_file in one_value["value"]:
            file_path = dir_path + one_file["file_Path"][1:]
            print("--file_path--", file_path)
            if os.path.exists(file_path):
                continue
            file_duration = one_file["duration"]/1000
            # file_name = os.path.split(file_path)[-1]
            for one_key in video_info.keys():
                if abs(file_duration - one_key) < 200:
                    os.rename(video_info[one_key], file_path)


def update_draft_content(dir_path):
    """
    更新draft_content。json文件
    :param dir_path draft_content.json文件存放的文件夹
    :return:
    """
    draft_content_s = os.path.join(jianying_template_path, "draft_content.json")
    draft_content_t = os.path.join(dir_path, "draft_content.json")
    if not os.path.exists(draft_content_s):
        return False
    if not os.path.exists(draft_content_t):
        return False
    # draft_meta_info 文件
    with open(draft_content_s, "r", encoding="utf-8") as file_hand:
        data_draft_content_s = json.loads(file_hand.read())
    with open(draft_content_t, "r", encoding="utf-8") as file_hand:
        data_draft_content_t = json.loads(file_hand.read())
    data_draft_content_t["last_modified_platform"] = data_draft_content_s["last_modified_platform"]

    with open(draft_content_t, "w", encoding="utf-8") as file_hand:
        json.dump(data_draft_content_t, file_hand)


def update_source_json(dir_path, source_dir):
    # draft_agency_config.json
    # draft_content.json
    # draft_meta_info.json

    draft_agency_config_s = os.path.join(dir_path, "draft_agency_config.json")
    draft_agency_config_t = os.path.join(source_dir, "draft_agency_config.json")

    draft_meta_info_s = os.path.join(dir_path, "draft_meta_info.json")
    draft_meta_info_t = os.path.join(source_dir, "draft_meta_info.json")

    draft_content_s = os.path.join(dir_path, "draft_content.json")
    draft_content_t = os.path.join(source_dir, "draft_content.json")

    # 拷贝文件
    if os.path.exists(draft_agency_config_s):
        shutil.copy(draft_agency_config_s, draft_agency_config_t)
    if os.path.exists(draft_content_s):
        shutil.copy(draft_content_s, draft_content_t)
    if os.path.exists(draft_meta_info_s):
        shutil.copy(draft_meta_info_s, draft_meta_info_t)
    if not os.path.exists(draft_content_t):
        return None

    video_path_s = os.path.join(dir_path, "videos")
    audios_path_s = os.path.join(dir_path, "audios")
    materials_path_s = os.path.join(dir_path, "materials")
    if os.path.exists(video_path_s):
        shutil.copytree(video_path_s, os.path.join(source_dir, "videos"))
    if os.path.exists(audios_path_s):
        shutil.copytree(audios_path_s, os.path.join(source_dir, "audios"))
    if os.path.exists(materials_path_s):
        shutil.copytree(materials_path_s, os.path.join(source_dir, "materials"))

    if not os.path.exists(draft_agency_config_t):
        print("文件不存在:", draft_agency_config_t)
        return None

    # 修改draft_agency_config 文件
    with open(draft_agency_config_t, "r", encoding="utf-8") as file_hand:
        draft_agency_config = json.loads(file_hand.read())

    all_file = OrderedDict()
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            all_file[file] = os.path.join(root, file)
    if draft_agency_config["marterials"]:
        for one_path in draft_agency_config["marterials"]:
            file_name = os.path.split(one_path["source_path"])[-1]
            if file_name in all_file.keys():
                one_path["source_path"] = all_file[file_name]
    # 写json文件
    print(draft_agency_config)
    with open(draft_agency_config_t, "w", encoding="utf-8") as file_hand:
        json.dump(draft_agency_config, file_hand)

    # draft_meta_info 文件
    with open(draft_meta_info_t, "r", encoding="utf-8") as file_hand:
        draft_meta_info = json.loads(file_hand.read())

    draft_meta_info["draft_fold_path"] = source_dir
    draft_meta_info["draft_root_path"] = source_dir
    draft_meta_info["draft_removable_storage_device"] = source_dir[:2]

    with open(draft_meta_info_t, "w", encoding="utf-8") as file_hand:
        json.dump(draft_meta_info, file_hand)


def run_logic(temp_dir_path):
    # 解压zip包
    all_zip = get_all_zip(source_template_dir)
    my_zip = CFile_zip()
    zip_file_dir_list = []

    # for one_zip in all_zip:
    #     file_name = os.path.splitext(os.path.split(one_zip)[-1])[0]
    #     if os.path.exists(os.path.join(un_zip_dir, file_name)):
    #         zip_file_dir_list.append(os.path.join(un_zip_dir, file_name))
    #         continue
    #     new_dir_name = os.path.join(un_zip_dir, file_name+"_1")
    #     if os.path.exists(new_dir_name):
    #         shutil.rmtree(new_dir_name)
    #     my_zip.File_unzip(one_zip, new_dir_name)
    #     # 重命名第一级目录
    #     # print(os.listdir(new_dir_name)[0])
    #     old_name = os.path.join(new_dir_name, os.listdir(new_dir_name)[0])
    #     new_name = os.path.join(new_dir_name, file_name)
    #     os.rename(old_name, new_name)
    #     # 拷贝到根目录吧
    #     if os.path.exists(os.path.join(un_zip_dir, file_name)):
    #         shutil.rmtree(os.path.join(un_zip_dir, file_name))
    #     shutil.copytree(new_name, os.path.join(un_zip_dir, file_name))
    #     shutil.rmtree(new_dir_name)
    #
    #     zip_file_dir_list.append(os.path.join(un_zip_dir, file_name))

    zip_file_dir_list = []
    for root, dirs, files in os.walk(temp_dir_path):
        for dir in dirs:
            full_path = os.path.join(root, dir)
            json_path = os.path.join(full_path, "draft_content.json")
            if os.path.exists(json_path):
                zip_file_dir_list.append(full_path)
    print(zip_file_dir_list)

    for one_dir in zip_file_dir_list:
        try:
            # update_source_video_name(one_dir)
            new_dir_name = os.path.split(one_dir)[-1]
            source_dir = copy_source_project(new_dir_name)
            update_source_json(one_dir, source_dir)
        except:
            print(traceback.format_exc())
        try:
            update_draft_content(source_dir)
        except:
            print(traceback.format_exc())


if __name__ == '__main__':
    # 剪影中文
    # jianying_project_path = r"C:\Users\31447\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft"
    # jianying_template_path = r"C:\Users\31447\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\8月16日"

    # capcut
    jianying_project_path = r"C:\Users\31447\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft"
    jianying_template_path = r"C:\Users\31447\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\0823"

    source_template_dir = r"E:\Documents\capcut资源\源文件\2023年01月19日更新-共15套"

    un_zip_dir = "D:\jianying_template"

    temp_dir_path = r"E:\剪影工程模板-capcut\2022年07月24日更新-共80套【源文件】\2022年7月24日更新-共80套【源文件】\剪映竖屏模板-11【源文件】"

    run_logic(temp_dir_path)

    # update_source_video_name(r"C:\Users\31447\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\N289-春节祝福【兔年春节】-横屏-0分30秒")
    # get_all_zip(source_template_dir)
    # update_source_json(r"C:\Users\31447\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\8月16日-2", r"C:\Users\31447\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\8月16日")