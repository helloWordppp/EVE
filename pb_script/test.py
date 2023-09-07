# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:test.py
@className:
@Create Data:2023/8/18 9:02 14:08
@Description:

"""
import os
import time

def find_files(path, suffix):
    result = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(suffix):
                result.append(os.path.join(root, file))
    return result

def find_dirs(path, suffix):
    result = []
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            if dir.endswith(suffix):
                result.append(os.path.join(root, dir))
    return result


