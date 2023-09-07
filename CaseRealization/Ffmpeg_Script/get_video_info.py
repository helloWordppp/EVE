# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:get_video_info_to_excel.py
@className:
@Create Data:2020/12/29 9:42
@Description:

"""
import os
import subprocess
import json
import sys
import json
from collections import OrderedDict
from CaseRealization.Ffmpeg_Script.ffmpeg_order import CFfmperOrder
from CaseRealization.Public.logging_print import MyLogPrint


class CGetVideoInfo:
    """
    获取视频信息
    """

    def __init__(self, my_log=None):
        """
        初始化函数
        :param my_log: 日志输出对象
        """
        self.dir_path, _ = os.path.split(sys.argv[0])
        if my_log is None:
            log_path = os.path.join(self.dir_path, "Log")
            if not os.path.exists(log_path):
                os.makedirs(log_path)
            log_path_full = os.path.join(log_path, "CWritePmonitorExcel.log")
            self.my_log = MyLogPrint(log_path_full)
        else:
            self.my_log = my_log

    def Get_video_info(self, video_path: str) -> dict:
        """
        获取视频的所有信息返回一个字典
        :param video_path:
        :return:
        """
        if not os.path.exists(video_path):
            return OrderedDict([("format_info", {}), ("streams_info", []), ("frames_info", [])])
        format_info = self.Get_video_show_format(video_path)  # 这个是 dict
        streams_info = self.Get_video_show_streams(video_path)  # 这个是list
        # frames_info = self.Get_video_show_frames(video_path)  # 这个是list
        # video_info = OrderedDict([("format_info", format_info), ("streams_info", streams_info),
        #                           ("frames_info", frames_info)])
        video_info = OrderedDict([("format_info", format_info), ("streams_info", streams_info)])

        return video_info

    def Get_video_show_format(self, video_path: str) -> dict:
        """
        获取视频文件的  format信息
        :param video_path:
        :return:
        """
        my_ffmpeg = CFfmperOrder()
        inputs = {video_path: None}
        global_options = '-of json -show_format'
        show_format_info = my_ffmpeg.Run_ffprobe_order(global_options, inputs)

        return show_format_info["format"]

    def Get_video_show_streams(self, video_path: str) -> list:
        """
        获取视频文件的 streams 信息
        :param video_path:
        :return:
        """
        my_ffmpeg = CFfmperOrder()
        inputs = {video_path: None}
        global_options = '-of json -show_streams'
        show_streams_info = my_ffmpeg.Run_ffprobe_order(global_options, inputs)

        return show_streams_info["streams"]

    def Get_video_show_frames(self, video_path: str) -> list:
        """
        frames
        :param video_path:
        :return:
        """
        my_ffmpeg = CFfmperOrder()
        inputs = {video_path: None}
        global_options = '-of json -show_frames'
        show_streams_info = my_ffmpeg.Run_ffprobe_order(global_options, inputs)

        return show_streams_info["frames"]

    def run_process(self, cmd_order: str) -> list:
        """
        调用Media info获取视频信息
        :param cmd_order: 命令行
        :return:视频信息
        """
        # subprocess.Popen(cmd_order, subprocess.PIPE, stdout=subprocess.stdout, stderr=subprocess.stderr)
        # cmd_order = '{0}'.format(TestRecordScreenPath)
        # EreProcess = subprocess.Popen(
        #     cmd_order,
        #     shell=False,
        #     stdin=subprocess.PIPE,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE
        # )
        try:
            process = subprocess.Popen(
                cmd_order, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=None
            )
        except:
            import traceback
            print(traceback.format_exc())
            raise Exception("run error")
        try:
            process.wait(timeout=30)
            out = process.stdout.read()
            if process.returncode != 0:
                raise Exception(cmd_order, process.returncode, out[0], out[1])
            out = json.loads(out)
            print(out)

            return out["media"]["track"]
        except:
            return []

    def run_program(self, cmd_order: str, wait=True, time_out=100) -> int:
        """
        运行一个进程并返回pid  如果pid为0表示失败
        :param cmd_order:
        :param wait:
        :param time_out:
        :return:
        """
        try:
            self.my_log.print_info(cmd_order)
            cmd_order = '{0}'.format(cmd_order)
            process = subprocess.Popen(
                cmd_order,
                shell=False,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.my_log.print_info(process.pid)
        except:
            self.my_log.print_info("运行程序失败")
            return 0
        if wait:
            process.wait(timeout=time_out)

        return process.pid

    def Get_video_info_mediainfo(self, video_path: str, json_name=None) -> list:
        """
        获取视频的所有信息返回一个字典 通过mediaifo 命令行
        :param video_path:
        :return:
        """

        dir_path, _ = os.path.split(sys.argv[0])
        mediainfo_path = os.path.join(dir_path, "res", "MediaInfo", "MediaInfo.exe")
        if not os.path.exists(mediainfo_path):
            self.my_log.print_info("mediainfo_path is not exists.", mediainfo_path)
            return None
        # print(video_path)
        if json_name is None:
            _, new_json = os.path.split(video_path)
            new_json = new_json + ".json"
        else:
            new_json = json_name + ".json"
        # print(new_json)
        temp_json = os.path.join(dir_path, "result", "temp_json", new_json)
        if os.path.exists(temp_json):
            os.remove(temp_json)
        if not os.path.exists(os.path.join(dir_path, "result", "temp_json")):
            os.makedirs(os.path.join(dir_path, "result", "temp_json"))

        cmd = '"{0}" "{1}" --Output=JSON --LogFile="{2}"'.format(mediainfo_path, video_path, temp_json)
        # self.my_log.print_info("cmd_order:", cmd)
        self.run_program(cmd)

        if not os.path.exists(temp_json):
            self.my_log.print_info("mediainfo_path is not exists. run mediainfo:", mediainfo_path)
            return None

        with open(temp_json, "r", encoding="utf-8") as file_handle:
            result_dict = json.load(file_handle)

        return result_dict["media"]["track"]
