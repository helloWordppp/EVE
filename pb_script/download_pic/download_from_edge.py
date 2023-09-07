# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:download_from_edge.py
@className:
@Create Data:2023/8/17 15:42 14:08
@Description:

"""
import time
import os
import sys
import traceback
import requests
import urllib.request
import re


headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
    }


def download_file(save_file_path, url_path):
    """
    下载文件
    :param save_file_path:
    :param url_path:
    :return:
    """
    file_dir = os.path.split(save_file_path)[0]
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    try:
        if os.path.exists(save_file_path):
            os.remove(save_file_path)

        url_file = requests.get(url_path)
        data = url_file.content
        # print(data)
        open(save_file_path, "wb").write(data)
    except:
        print(traceback.format_exc())
        return False

    return True


def get_url_from_txt(txt_path):
    """

    :return:
    """
    with open(txt_path, "r", encoding="UTF-8") as file_hand:
        all_data = file_hand.read()

    data_list = re.findall('<li><a(.*?)</a></li>', all_data)
    urls = []
    # print(data_list)
    for item in data_list:
        # print(item)
        temp_url_str = re.findall('href="(.*?)"', item)[0]
        print(temp_url_str)
        temp_list = temp_url_str.split(";")
        for tem_url in temp_list:
            if tem_url.startswith("mediaurl="):
                url = tem_url.replace("mediaurl=", "").replace("&amp", "").replace("%3a", ":").replace("%2f", "/")
                urls.append(url)
    print(urls)
    return urls


def run_logic(html_path):
    """

    :param html_path:
    :return:
    """
    dir_path = os.path.split(sys.argv[0])[1]
    pic_path = os.path.join(r"E:\视频剪辑素材\图片素材", "美国")
    if not os.path.exists(pic_path):
        os.makedirs(pic_path)
    urls = get_url_from_txt(html_path)
    print("---all pic---", len(urls))
    i = 1
    for url in urls:
        print("-----当前第:", i)
        i += 1
        time_now = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time())) + ".jpg"
        full_save_path = os.path.join(pic_path, time_now)
        if not download_file(save_file_path=full_save_path, url_path=url):
            print("下载失败:", url)
            time.sleep(1)
            download_file(save_file_path=full_save_path, url_path=url)


if __name__ == '__main__':
    html_path = r"D:\Downloads\edge-pic\美国美女\美国美女 - Bing images.html"
    run_logic(html_path)
    html_path = r"D:\Downloads\edge-pic\美国美女\American Handsome Boy - Bing images.html"
    run_logic(html_path)
    html_path = r"D:\Downloads\edge-pic\search.htm"
    run_logic(html_path)
    html_path = r"D:\Downloads\edge-pic\search (1).htm"
    run_logic(html_path)

