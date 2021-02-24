# 类别数量
num_classes = 56
# 卡片识别单元
words=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '=', '(', ')', '+', '-', '/', '*',
          'A', 'B', 'C','D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
          'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '停车', '前进', '右转', '左转', '掉头',
          '橙色', '淡蓝色', '粉色', '红色', '绿色', '蓝色', '黄色', '黑色']

model_path = './kapian.h5'

import os
import cv2
import dlib
import numpy as np
from itertools import combinations,permutations
from imutils.perspective import four_point_transform
import imutils
from PIL import Image, ImageDraw, ImageFont
from statistics import mode
import math

from keras.preprocessing import image
from keras.layers import Dense
from keras.layers import MaxPooling2D
from keras.layers import Input
from keras.layers import Conv2D
from keras.layers import Flatten
from keras.layers import Dropout
from keras.models import Model
from keras.models import load_model

size_jx = 100
input_shape = (size_jx, size_jx, 3)




# 基本参数（不需要修改）
cur_flag = 1
kapian_arr = []
chuxian_num = 7
no_num = 15
zhanshi = 3
kapian_cur = 'kapian'

cur_flag2 = 1
kapian_arr2 = []
chuxian_num2 = 7
no_num2 = 15
zhanshi2 = 3
kapian_cur2 = 'kapian'
jisuan = 0
jisuan_t = 0
fuhao = []
gongshi =''
ii = 0

def rotateRect(img,points):
    color=(0,255,0)
    for i in range(4):
        cv2.line(img,tuple(points[i]),tuple(points[(i+1)%4]),color)

# 网络部分

net = {}

net['input'] = Input(shape=input_shape)
# Block1
net['conv1'] = Conv2D(32, 3,
                      activation='relu',
                      padding='same',
                      name='conv1')(net['input'])
net['pool1'] = MaxPooling2D(4, 4, padding='same',
                            name='pool1')(net['conv1'])

# Block2
net['conv2'] = Conv2D(128, 3,
                      activation='relu',
                      padding='same',
                      name='conv2')(net['pool1'])
net['pool2'] = MaxPooling2D(4, 4, padding='same',
                            name='pool2')(net['conv2'])

# Block3
net['conv3'] = Conv2D(256, 3,
                      activation='relu',
                      padding='same',
                      name='conv3')(net['pool2'])
net['pool3'] = MaxPooling2D(3, 3, padding='same',
                            name='pool3')(net['conv3'])


# fc层
net['pool3_drop'] = Dropout(0.5, name='pool3_drop')(net['pool3'])
net['pool3_drop_fla'] = Flatten(name='pool3_drop_fla')(net['pool3_drop'])
net['fc1'] = Dense(512, activation='relu', name='fc1')(net['pool3_drop_fla'])

net['fc1_drop'] = Dropout(0.25, name='fc1_drop')(net['fc1'])
net['fc2'] = Dense(512, activation='relu', name='fc2')(net['fc1_drop'])

net['out'] = Dense(num_classes, activation='softmax', name='out')(net['fc2'])

# 创建model
model = Model(net['input'], net['out'])

model.load_weights(model_path)



# 边框检测以及简单过滤
def f(img):
    row,col,c=img.shape
    img_gray=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    ret,img_thre=cv2.threshold(img_gray,132,255,cv2.THRESH_BINARY)
    kernel=np.ones([5,5])
    img_erode = cv2.erode(img_thre, kernel)
    img_dilate=cv2.dilate(img_erode,kernel)
    # cv2.imshow('123', img_thre)
    # cv2.imshow('456', img_dilate)
    contours,hierarchy = cv2.findContours(img_dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#     _,contours,hierarchy = cv2.findContours(img_dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    count=0
    images=[]
    points=[]
    

    '''
        定位三点进行旋转

    '''
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#         warped = four_point_transform(gray, docCnt.reshape(4, 2))
    # 对灰度图应用大津二值化算法
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    # 在二值图像中查找轮廓，然后初始化题目对应的轮廓列表
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    cnts,_ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#         cnts = cnts[1] if imutils.is_cv3() else cnts[0]
    questionCnts = []
#     print(len(cnts))
    # 对每一个轮廓进行循环处理
    for c in cnts:
        # 计算轮廓的边界框，然后利用边界框数据计算宽高比
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        # 构造只有当前气泡轮廓区域的掩模图像
        mask = np.zeros(thresh.shape, dtype="uint8")
        cv2.drawContours(mask, [c], -1, 255, -1)

        # 对二值图像应用掩模图像，然后就可以计算气泡区域内的非零像素点。
        mask = cv2.bitwise_and(thresh, thresh, mask=mask)
        total = cv2.countNonZero(mask)
#         print(total)
        ttt = np.mean(mask)
#             print(ttt)

        # 大小、像素点、比例、参数设置处
        if w <= 60 and h <= 60 and w >= 10 and h >= 10 and total > 150 and ar >= 0.9 and ar <= 1.1:
            tmp_yx = np.array([int(x+w/2),int(y+h/2),int(w/2)])
            questionCnts.append(tmp_yx)
    if len(questionCnts) != 3:
        return None
#     print(questionCnts)

    for j in range(3):
        tmp_point1 = questionCnts[(0+j)%3]
        tmp_point2 = questionCnts[(1+j)%3]
        tmp_point3 = questionCnts[(2+j)%3]



        if ((math.sqrt(math.pow(tmp_point1[0] - tmp_point2[0], 2) + math.pow(tmp_point1[1] - tmp_point2[1], 2)) / \
        math.sqrt(math.pow(tmp_point1[0] - tmp_point3[0], 2) + math.pow(tmp_point1[1] - tmp_point3[1], 2))) > 0.8) & \
        ((math.sqrt(math.pow(tmp_point1[0] - tmp_point2[0], 2) + math.pow(tmp_point1[1] - tmp_point2[1], 2)) / \
        math.sqrt(math.pow(tmp_point1[0] - tmp_point3[0], 2) + math.pow(tmp_point1[1] - tmp_point3[1], 2))) < 1.2):
            point1 = tmp_point1
            point2 = tmp_point2
            point3 = tmp_point3
            img_hongdian = img.copy()
            cv2.circle(img_hongdian, (point1[0], point1[1]), 1, (0, 0, 255), point1[2]*12)
#                     print('nihaonihao')
            break
    
    '''
        三点定位
    '''
    
    for cnt in contours:
#         print(cnt)
#         print(cnt.shape)
#         print('________________________________')
        # x, y, w, h = cv2.boundingRect(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        if x<10 or y<10  or (x+w)>(col-10) or (y+h)>(row-10):continue#边界过滤
#         if abs(w/(h*1.0)-1)>0.3:
# #             print(abs(w/(h*1.0)-1))
# #             print('正方形过滤')
#             continue#正方形过滤
        sclae=w*h/(row*col)
        if sclae<0.03 or sclae>0.8:
#             print(sclae)
#             print('比例过滤')
            continue#比例过滤

        if (w <= 80 and h <= 80):
#             print('大小过滤')
            continue#大小过滤

        rect = cv2.minAreaRect(cnt)
        x = int(rect[0][0])
        y = int(rect[0][1])
        w = int(rect[1][0])
        h = int(rect[1][1])
        jiaodu = int(rect[2])

        if abs(w/(h*1.0)-1)>0.3:
            # print('正方形过滤')
            continue#正方形过滤

#         if abs(jiaodu) > 30:
#             # print('角度过滤')
#             continue#角度过滤


        box = cv2.boxPoints(rect)
        warped = four_point_transform(img, box)#获取卡片
        warped_hongdian = four_point_transform(img_hongdian, box)#获取卡片
        ttx = point1[2]
        tty = point1[2]*2
        zuoshang = warped_hongdian[ttx:tty, ttx:tty]
        youshang = warped_hongdian[ttx:tty, -tty:-ttx]
        zuoxia = warped_hongdian[-tty:-ttx, ttx:tty]
        youxia = warped_hongdian[-tty:-ttx, -tty:-ttx]
        tmp_war = warped
        
        if np.mean(youshang[:,:,2]) > 222:
            tmp_war=np.rot90(tmp_war)
#             print('1111111111111111111111111111111')
        elif np.mean(youxia[:,:,2]) > 222:
            tmp_war=np.rot90(tmp_war)
            tmp_war=np.rot90(tmp_war)
#             print('222222222222222222222222222222')
        elif np.mean(zuoxia[:,:,2]) > 222:
            tmp_war=np.rot90(tmp_war)
            tmp_war=np.rot90(tmp_war)
            tmp_war=np.rot90(tmp_war)
#             print('333333333333333333333333333333')
        elif np.mean(zuoshang[:,:,2]) > 222:
            tmp_war = tmp_war
        else:
            continue
            
#         cv2.imshow('warped', tmp_war)
#         cv2.imshow('youshang', youshang)
#         cv2.imshow('zuoshang', zuoshang)
#         cv2.imshow('youxia', youxia)
#         cv2.imshow('zuoxia', zuoxia)
#         cv2.imshow('hongdian', warped)
        
        temp=img[y:y+h,x:x+w,:]
        images.append(tmp_war)
        points.append(box)
        count+=1
    if len(images)<=0:
        return None
    else:
        return images, points

# 支持中文显示
def add_chinese(img,name,text_position):

    img_PIL = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
 
    font = ImageFont.truetype('simhei.ttf', 30, encoding="utf-8")
    
    draw = ImageDraw.Draw(img_PIL)
    draw.text(text_position, '识别结果：' + name, font=font, fill=(255,0,0))

    img_OpenCV = cv2.cvtColor(np.asarray(img_PIL),cv2.COLOR_RGB2BGR)

    return img_OpenCV

def kapianshibie(frame):
    cards, points = f(frame)
#     print(len(cards))
    for i in range(len(cards)):
        pic = cv2.resize(cards[i], (100, 100))
        inputs = [image.img_to_array(pic)]
        inputs = np.array(inputs)

        inputs /= 255.
        out = model.predict(inputs, batch_size=1)
        out = np.array(out)
        
        index = np.argmax(out)
        gl = out[0][index]
#         print(gl)
        if gl < 0.8:
            return frame, ' ', ' ', ' '
        
        out = words[index]
#         print(out)
        if out == '黄色':
            return frame, ' ', ' ', ' '
        tmp_i = i
        rotateRect(frame, points[i])
    return frame, out, gl, index, points[tmp_i]

def kapian_out(frame, kpcishu, wkpcishu, moshi = 1):
    global no_num
    global cur_flag
    global kapian_arr
    global chuxian_num
    global zhanshi
    global kapian_cur

    try:
        frame_c = frame.copy()
        frame_c, out, gl, index, tmp_point = kapianshibie(frame_c)
#         print(gl)
        if out != ' ' and moshi:
            if no_num <= 0:
                cur_flag = 1
                chuxian_num = kpcishu
                no_num = wkpcishu
                kapian_cur = 'kapian'
            if chuxian_num == 0 and cur_flag:
                # print(kapian_cur)
                cur_flag = 0
                return kapian_cur, frame_c, (0,0)
            if chuxian_num in range(1,kpcishu-2):
                if out == kapian_cur:
                    chuxian_num -= 1
            if chuxian_num in [kpcishu-2, kpcishu-1]:
                if out == kapian_cur:
                    chuxian_num -= 1
                else:
                    chuxian_num = kpcishu
            if chuxian_num == kpcishu:
                kapian_cur = out
                chuxian_num -= 1

            frame_c = add_chinese(frame_c, out, (0, 60))
            return 0, frame_c, (0,0)
        zx,zy=int((tmp_point[0,0]+tmp_point[2,0])/2), int((tmp_point[0,1]+tmp_point[2,1])/2)
        if not moshi:
            frame_c = add_chinese(frame_c, '({}, {})'.format(zx, zy), (0, 60))
        return 0, frame_c, (zx, zy)
            # cv2.imshow('out', frame_c)
    except Exception as e:
        no_num -= 1
#         print(e)
        return 0, frame, (0,0)
        # cv2.imshow('out', frame)