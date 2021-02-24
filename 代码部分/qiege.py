# created at 2018-01-22
# updated at 2018-09-29

# Author:   coneypo
# Blog:     http://www.cnblogs.com/AdaminXie
# GitHub:   https://github.com/coneypo/Dlib_face_cut

import dlib         # 人脸识别的库dlib
import numpy as np  # 数据处理的库numpy
#import opencv as cv2
#import numpy.core.multiarray
import cv2         # 图像处理的库OpenCv
import os

# Dlib 检测器
detector = dlib.get_frontal_face_detector()
#predictor = dlib.shape_predictor()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
list=os.listdir("faceimg/newface/-1")

for g in range(1,11):# 读取图像
    flag = 0
    print(g)
    path = "faceimg/newface/-1/"
    img = cv2.imread(path+str(g)+".jpg")
    img = cv2.resize(img, (1000, 900), interpolation=cv2.INTER_AREA)  # 将图片变成固定大小1000,900,怕有的图里人脸割出来太大，稍微收缩下
    # Dlib 检测
    dets = detector(img, 1)

    print("人脸数：", len(dets), "\n")
    if len(dets)==0:
        print("none");
        continue
    # 记录人脸矩阵大小
    height_max = 0
    width_sum = 0

    # 计算要生成的图像 img_blank 大小
    for k, d in enumerate(dets):
        if (d.top() < 0 or d.left()< 0) :
            flag=1
        # 计算矩形大小
        # (x,y), (宽度width, 高度height)
        pos_start = tuple([d.left(), d.top()])
        pos_end = tuple([d.right(), d.bottom()])

        # 计算矩形框大小
        height = d.bottom()-d.top()
        width = d.right()-d.left()

        # 处理宽度

        if height > width_sum:
            width_sum = height
        else:
            width_sum = width_sum

        # 处理高度
        if height > height_max:
            height_max = height
        else:
            height_max = height_max

    # 绘制用来显示人脸的图像的大小
    if(flag==1):
        continue
    print("窗口大小："
          , '\n', "高度 / height:", height_max
          , '\n', "宽度 / width: ", width_sum)

    # 生成用来显示的图像
    img_blank = np.zeros((height_max+5, width_sum+5, 3), np.uint8)

    # 记录每次开始写入人脸像素的宽度位置
    blank_start = 0
    # 将人脸填充到img_blank
    for k, d in enumerate(dets):

        height = height_max#d.bottom()-d.top()
        width = width_sum#d.right()-d.left()
        print(d.top())
        print(d.left())
        # 填充
        try:
         for i in range(height-1):
            for j in range(width-1):
                #print(str(blank_start)+str(i)+"*****"+str(blank_start)+str(j))
                #print(str(d.top())+str(i)+"*****"+str(d.left())+str(j))
                 img_blank[blank_start+i][blank_start+j] = img[d.top()+i][d.left()+j]
        except:
            break
        # 调整图像
        blank_start += width
        img_blank = cv2.resize(img_blank, (200, 200), interpolation=cv2.INTER_AREA)  # 将图片变成固定大小200,200,这步可以不用,自己选择
    cv2.namedWindow("img_faces")#, 2)
    cv2.imshow("img_faces", img_blank)
    cv2.imwrite("faceimg/newface/-1/"+str(g)+"lala.jpg", img_blank)
   # cv2.waitKey(0)