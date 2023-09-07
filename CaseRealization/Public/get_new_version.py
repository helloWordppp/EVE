# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:get_new_version.py
@className:
@time:2019/7/17 9:09
@function:

"""
import os
import shutil
import traceback
import sys
from CaseRealization.Public.get_system_info import Get_max_free_partition
from CaseRealization.Public.read_ini import ConfigRead
from CaseRealization.Public.get_system_info import set_network_connect, set_network_connect_in, set_network_connect_in172


class CGetNewVersion:
    """
    获取新版本
    """
    def __init__(self):
        dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
        ini_file = os.path.join(dirname, r"Config\config.ini")
        if not os.path.exists(ini_file):
            raise Exception("ini file not exist!", ini_file)
        my_ini = ConfigRead()
        my_ini.GetData(ini_file)
        self.server_path = my_ini.get("server_path", "path")
        self.product_name = my_ini.get("product_name", "name")
        self.package_name = my_ini.get("package_name", "name")
        self.language = my_ini.get("language", "lang")

        if self.server_path.startswith(r"\\192.168.1.110"):
            print("set_network_connect")
            set_network_connect()
        elif self.server_path.startswith(r"\\192.168.0.242"):
            print("set_network_connect_in")
            set_network_connect_in()
        elif self.server_path.startswith(r"\\172.17.188.242"):
            print("set_network_connect_in172")
            set_network_connect_in172()

    def Copy_version(self):
        """

        :return:
        """
        loacl_path = os.path.join(Get_max_free_partition(), "easeus_product_package", self.product_name)
        if not os.path.exists(loacl_path):
            os.makedirs(loacl_path)

        # local_new = self.Get_dir_last_dir(loacl_path)
        # net_path = r"\\192.168.1.110\产品发布\临时版本\PCTrans\11.0"
        net_path = self.server_path
        net_new = self.Get_dir_last_dir(net_path)
        if os.path.exists(os.path.join(loacl_path, net_new)) and \
                not os.listdir(os.path.join(loacl_path, net_new)):
            os.rmdir(os.path.join(loacl_path, net_new))
        if not os.path.exists(os.path.join(loacl_path, net_new)):
            try:
                shutil.copytree(os.path.join(net_path, net_new), os.path.join(loacl_path, net_new))
            except:
                if not os.path.exists(os.path.join(loacl_path, net_new)):
                    os.makedirs(os.path.join(loacl_path, net_new))
                cmd = r'xcopy "{0}" "{1}" /s /e /y'.format(os.path.join(net_path, net_new),
                                                           os.path.join(loacl_path, net_new))
                print(cmd)
                ss = os.popen(cmd)
                print(ss.read())
                if os.listdir(os.path.join(loacl_path, net_new)).__len__() > 0:
                    return os.path.join(loacl_path, net_new)
                error = traceback.format_exc()
                print(error)
                raise Exception("拷贝文件失败")
        else:
            return None
        return os.path.join(loacl_path, net_new)

    def Get_dir_last_dir(self, dir_path):
        """

        :param dir_path:
        :return:
        """
        loacl_version = None
        tem_new = 0
        for item in os.listdir(dir_path):
            if item.startswith("download"):
                continue
            chaild_path = os.path.join(dir_path, item)
            if not os.path.isdir(chaild_path):
                continue
            child_file_list = []
            for temp_item in os.listdir(chaild_path):
                if os.path.isdir(os.path.join(chaild_path, temp_item)):
                    continue
                if os.path.splitext(temp_item)[1].lower() == ".exe":
                    child_file_list.append(os.path.join(chaild_path, temp_item))
            if child_file_list.__len__() > 0:
                if os.path.getmtime(child_file_list[0]) > tem_new:
                    tem_new = os.path.getmtime(chaild_path)
                    loacl_version = item
        print(loacl_version)
        return loacl_version


if __name__ == '__main__':
    path = r"\\192.168.1.110\产品发布\临时版本\PCTrans\10.5"
    test = CGetNewVersion()
    test.Get_dir_last_dir(path)
