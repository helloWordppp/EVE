# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:file_zip.py
@className:
@time:2019/6/10 13:47
@function:
文件、文件夹 压缩和解压缩操作
"""

import os
import stat
import logging
import zipfile


class CFile_zip:
    """
    文件压缩和解压缩
    """
    def File_zip(self, source, output, cover=True):
        """
        文件、文件夹压缩
        :param source: 需要压缩的文件或者文件夹
        :param output: 输出的zip文件完整路劲
        :param cover: 当output文件存在时是否覆盖
        :return: 成功 True 失败 false
        """
        if not os.path.exists(source):
            print("source file not exists")
            return False
        if os.path.exists(output):
            print("output file is exists")
            if cover:
                try:
                    print("remove the output file")
                    os.remove(output)
                except Exception:
                    print("remove output file error:")
                    print(logging.exception(Exception))
                    return False
            else:
                return False

        # ZIP_DEFLATED:表示压缩，还有一个参数：ZIP_STORE：表示只打包，不压缩。这个Linux中的gz跟tar格式有点类似.
        zip = zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED)
        try:
            if os.path.isdir(source):
                for path, dir_list, file_list in os.walk(source):
                    zip_path = path.replace(source, "")
                    for one_file in file_list:
                        # 大于10MB的文件跳过
                        if os.path.getsize(os.path.join(path, one_file)) > 1024*1024*10:
                            continue
                        zip.write(os.path.join(path, one_file), os.path.join(zip_path, one_file))
            elif os.path.isfile(source):
                zip.write(source, os.path.split(source)[1])
        except Exception as e:
            print("zip file has error")
            print(logging.exception(e))
            zip.close()
            return False
        zip.close()
        return True

    def File_unzip(self, zip_file, save_path, cover=True):
        """
        解压缩zip文件
        :param zip_file: zip文件路径
        :param save_path: 文件保存路径
        :return: 解压成功失败
        """
        try:
            zip = zipfile.ZipFile(zip_file, "r")
            for file in zip.namelist():
                # print(os.path.join(save_path, file))
                if cover and os.path.exists(os.path.join(save_path, file)):
                    try:
                        os.chmod(os.path.join(file, save_path), stat.S_IWUSR)
                        os.remove(os.path.join(file, save_path))
                    except Exception as e:
                        print(logging.exception(e))
                        return False
                zip.extract(file, save_path)
            zip.close()
        except Exception:
            print(logging.exception(Exception))
            return False
        return True


if __name__ == '__main__':
    test = CFile_zip()
    test.File_zip(r"I:\PCT_Anti\PcTranse_Auto.exe", r"I:\PCT_Anti\1234.zip")
    # test.File_unzip(r"I:\PCT_Anti\123.zip", r"I:\PCT_Anti1")
