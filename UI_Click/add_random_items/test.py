# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:test.py
@className:
@Create Data:2023/9/6 18:28 14:08
@Description:

"""
import os
import cv2
import time
import numpy as np
from typing import Tuple

from collections import OrderedDict

#定义形状检测函数
def ShapeDetection(img, imgContour):
    contours,hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)  #寻找轮廓点
    for obj in contours:
        area = cv2.contourArea(obj)  #计算轮廓内区域的面积
        cv2.drawContours(imgContour, obj, -1, (255, 0, 0), 4)  #绘制轮廓线
        perimeter = cv2.arcLength(obj,True)  #计算轮廓周长
        approx = cv2.approxPolyDP(obj,0.02*perimeter,True)  #获取轮廓角点坐标
        CornerNum = len(approx)   #轮廓角点的数量
        x, y, w, h = cv2.boundingRect(approx)  #获取坐标值和宽度、高度

        #轮廓对象分类
        if CornerNum ==3: objType ="triangle"
        elif CornerNum == 4:
            if w==h: objType= "Square"
            else:objType="Rectangle"
        elif CornerNum>4: objType= "Circle"
        else:objType="N"

        cv2.rectangle(imgContour,(x,y),(x+w,y+h),(0,0,255),2)  #绘制边界框
        cv2.putText(imgContour,objType,(x+(w//2),y+(h//2)),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,0,0),1)  #绘制文字

def test():
    path = r'E:\MyProject\PythonProject\pythonProject\EVE\UI_Click\add_random_items\temp\pic\20230906182728_21.png'
    img = cv2.imread(path)
    imgContour = img.copy()

    imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转灰度图
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)  # 高斯模糊
    imgCanny = cv2.Canny(imgBlur, 60, 60)  # Canny算子边缘检测
    ShapeDetection(imgCanny, imgContour)  # 形状检测

    cv2.imshow("Original img", img)
    cv2.imshow("imgGray", imgGray)
    cv2.imshow("imgBlur", imgBlur)
    cv2.imshow("imgCanny", imgCanny)
    cv2.imshow("shape Detection", imgContour)

    cv2.waitKey(0)


# 获取图片坐标bgr值
def get_pix_bgr(image_path: str, x: int, y: int) -> Tuple[int, int, int]:
    """
    返回图片某一个点的rgb值   如果位置超过图片则会出现异常
    :param image_path:
    :param x:
    :param y:
    :return:
    """
    ext = os.path.basename(image_path).strip().split('.')[-1]
    if ext not in ['png', 'jpg']:
        raise Exception('format error')
    img = cv2.imread(image_path)
    # px = img[x, y]
    blue = img[y, x, 0]
    green = img[y, x, 1]
    red = img[y, x, 2]
    return red, green, blue


def get_pic_size(image_path: str) -> Tuple[int, int, int]:
    """
    获取图片尺寸
    :param image_path:
    :return:
    """
    ext = os.path.basename(image_path).strip().split('.')[-1]
    if ext not in ['png', 'jpg']:
        raise Exception('format error')
    img = cv2.imread(image_path)
    return img.shape  # [高|宽|像素值由三种原色构成]


def fund_the_item_local_in_track(all_rgb:OrderedDict, no_item_rgb=(23, 33, 41)) -> OrderedDict:
    """
    通过获取到的颜色点位，大致判断出轨道上item的起始和结束位置 该位置与all_rgb中的位置精度有关
    该位置为相对于图片的位置
    :param all_rgb:
    :param no_item_rgb: 没有节点时轨道的颜色值 判断是会允许有左右10个值的浮动
    :return:
    """
    all_item = []
    one_item = OrderedDict()
    for x in all_rgb.keys():
        if no_item_rgb[0] - 10 <= all_rgb[x][0] <= no_item_rgb[0] + 10 and \
            no_item_rgb[1] - 10 <= all_rgb[x][1] <= no_item_rgb[1] + 10 and \
            no_item_rgb[2] - 10 <= all_rgb[x][2] <= no_item_rgb[2] + 10:
            if len(one_item.keys()) > 0:
                all_item.append(one_item)
            one_item = OrderedDict()
            continue
        else:
            one_item[x] = all_rgb[x]

    if len(one_item.keys()) > 0 and one_item not in all_item:
        all_item.append(one_item)

    # print(all_item)
    return all_item


path = r'E:\MyProject\PythonProject\pythonProject\EVE\UI_Click\add_random_items\temp\pic\20230906182728_21.png'
sp = get_pic_size(path)
print(sp)

x = 20
y = 10

all_rgb = OrderedDict()
time_start = time.time()
while x <= sp[1]:
    # print(x, y)

    one = get_pix_bgr(image_path=path, x=x, y=y)
    all_rgb[x] = one
    x += 20


print(time.time() - time_start)
print(all_rgb)
print(fund_the_item_local_in_track(all_rgb))
