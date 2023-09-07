# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:ffmpeg_order.py
@className:
@Create Data:2020/11/25 14:51
@Description:

"""
import os
import sys
from ffmpy import FFmpeg, FFprobe
from subprocess import PIPE
import json


# from RecordWebpage.IniRead import CIniConfig


class CFfmperOrder:
    """"""

    def __init__(self):
        dir_path, _ = os.path.split(sys.argv[0])
        # self.ffpeg_exe_path = r"H:\Download\ffmpeg4.3.1\bin\ffmpeg.exe"
        # self.ffprobe_exe_path = r"H:\Download\ffmpeg4.3.1\bin\ffprobe.exe"
        # self.ffplay_exe_path = r"H:\Download\ffmpeg4.3.1\bin\ffplay.exe"
        self.ffpeg_exe_path = os.path.join(dir_path, r"ffmpeg\bin\ffmpeg.exe")
        self.ffprobe_exe_path = os.path.join(dir_path, r"ffmpeg\bin\ffprobe.exe")
        self.ffplay_exe_path = os.path.join(dir_path, r"ffmpeg\bin\ffplay.exe")
        if not os.path.exists(self.ffprobe_exe_path):
            raise Exception("ffprobe.exe is not found.{0}".format(self.ffprobe_exe_path))

    def Run_ffprobe_order(self, global_options: str, inputs: dict) -> dict:
        """
        运行ffprobe命令
        :param global_options: str
        :param inputs: dic
        :return:
        """
        # 构建FFmpeg命令行
        ff = FFprobe(
            executable=self.ffprobe_exe_path,
            # global_options='-of json -show_streams -select_streams v',
            # '-of json -show_streams'
            global_options=global_options,
            # {video_path: None}
            inputs=inputs,
        )
        # ffmpeg默认输出到终端, 但我们需要在进程中获取媒体文件的信息
        # 所以将命令行的输出重定向到管道, 传递给当前进程
        res = ff.run(stdout=PIPE, stderr=PIPE)
        # print(res)
        ffprobe_output_str = res[0]
        ffprobe_output_str = ffprobe_output_str.decode("gbk")
        ffprobe_output_dic = json.loads(ffprobe_output_str)
        # print(ffprobe_output_dic)
        # print(len(ffprobe_output_dic["streams"]))
        return ffprobe_output_dic

    def Run_ffmpeg_order(self, global_options: str, inputs: dict) -> dict:
        """
        运行ffmpeg命令
        :param global_options: str
        :param inputs: dic
        :return:
        """
        # 构建FFmpeg命令行
        ff = FFmpeg(
            executable=self.ffprobe_exe_path,
            # global_options='-of json -show_streams -select_streams v',
            # '-of json -show_streams'
            global_options=global_options,
            # {video_path: None}
            inputs=inputs,
        )
        # ffmpeg默认输出到终端, 但我们需要在进程中获取媒体文件的信息
        # 所以将命令行的输出重定向到管道, 传递给当前进程
        res = ff.run(stdout=PIPE, stderr=PIPE)
        # print(res)
        ffmpge_output_str = res[0]
        ffmpeg_output_dic = json.loads(ffmpge_output_str)
        # print(ffprobe_output_dic)
        # print(len(ffprobe_output_dic["streams"]))
        return ffmpeg_output_dic


def video_info(video_path):
    """
    接受视频路径, 读取视频信息
    :param video_path: 视频路径
    :return: 视频帧率
    """
    ffmpeg_executable = r"H:\Download\ffmpeg4.3.1\bin\ffmpeg.exe"
    ffprobe_executable = r"H:\Download\ffmpeg4.3.1\bin\ffprobe.exe"
    # 构建FFmpeg命令行
    ff = FFprobe(
        executable=ffprobe_executable,
        # global_options='-of json -show_streams -select_streams v',
        global_options='-of json -show_streams',
        inputs={video_path: None},
    )

    # ffmpeg默认输出到终端, 但我们需要在进程中获取媒体文件的信息
    # 所以将命令行的输出重定向到管道, 传递给当前进程
    res = ff.run(stdout=PIPE, stderr=PIPE)

    print(res)

    video_stream = res[0]

    print(video_stream)
    print(type(video_stream))

    # 解析视频流信息
    video_detail = json.loads(video_stream).get('streams')[0]

    # 获取视频实际帧率, 计算取整
    frame_rate = round(eval(video_detail.get('r_frame_rate')))

    print(frame_rate)

    # 返回码率
    return frame_rate


if __name__ == '__main__':
    video_path = r"C:\Users\pengbo\Documents\EaseUS\易我录屏助手\20201124_112345.mp4"

    user_choose = input("Enter the required information\n  "
                        "1-show_streams+show_format\n "
                        "2-show_streams+show_format+show_frames\n "
                        "3-show_streams+show_format+show_frames+show_packets\n")
    user_choose = int(user_choose)
    print("user choose is:", user_choose)

    file_list = sys.argv
    if file_list.__len__() != 2:
        video_path = input("input the file full path:\n")
    else:
        video_path = file_list[1]
    print("the file path is:", video_path)
    # video_info(video_path)

    test = CFfmperOrder()
    global_options = '-of json -show_streams'
    inputs = {video_path: None}
    print("get show_streams info")
    show_streams_info = test.Run_ffprobe_order(global_options, inputs)

    print("get show_format info")
    global_options = '-of json -show_format'
    show_format_info = test.Run_ffprobe_order(global_options, inputs)

    print("whit result to file")
    file_name = os.path.splitext(os.path.split(video_path)[1])[0]
    ini_file_path = os.path.join(os.getcwd(), "{0}.ini".format(file_name))
    if os.path.exists(ini_file_path):
        os.remove(ini_file_path)

    # my_ini = CIniConfig(ini_file_path)
    my_ini = open(ini_file_path, mode="w+", encoding="utf-8")
    my_ini.write("[show_format_info]\n")
    for key, value in show_format_info["format"].items():
        # my_ini.Set_section("show_format_info", key, value)
        one_line = "{0}={1}\n".format(key, value)
        my_ini.write(one_line)

    streams_num = 1
    for one_streams in show_streams_info["streams"]:
        my_ini.write("[show_streams_info_{0}]\n".format(streams_num))
        for key, value in one_streams.items():
            # my_ini.Set_section("show_streams_info_{0}".format(streams_num), key, value)
            one_line = "{0}={1}\n".format(key, value)
            my_ini.write(one_line)
        streams_num += 1

    if user_choose >= 2:
        global_options = '-of json -show_frames'
        print("get show_frames info")
        show_frames_info = test.Run_ffprobe_order(global_options, inputs)
        print("white the file show_frames")
        streams_num = 1
        for one_streams in show_frames_info["frames"]:
            my_ini.write("[show_frames_info_{0}]\n".format(streams_num))
            for key, value in one_streams.items():
                # my_ini.Set_section("show_streams_info_{0}".format(streams_num), key, value)
                one_line = "{0}={1}\n".format(key, value)
                my_ini.write(one_line)
            streams_num += 1

    if user_choose >= 3:
        global_options = '-of json -show_packets'
        print("get show_packets info")
        show_packets_info = test.Run_ffprobe_order(global_options, inputs)
        print("white the file show_packets")
        streams_num = 1
        for one_streams in show_packets_info["packets"]:
            my_ini.write("[show_packets_info_{0}]\n".format(streams_num))
            for key, value in one_streams.items():
                # my_ini.Set_section("show_packets_info_{0}".format(streams_num), key, value)
                one_line = "{0}={1}\n".format(key, value)
                my_ini.write(one_line)
            streams_num += 1

    my_ini.close()
    print(ini_file_path)
    input("get file info finish...")
