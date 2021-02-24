import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
import dazuiniao
from dazuiniao import add_chinese
from dazuiniao import kapian_out, predictper, biaoqing, genzong, lianxukapian
import time
import matplotlib
import matplotlib.backends.backend_tkagg

#界面相关
window_width=800
window_height=530
image_width=640
image_height=480
lb_x = 640
lb_y = 50
imagepos_x=-5
imagepos_y=50
youyi = 20
butpos_x0=0+youyi
butpos_x1=120+youyi
butpos_x2=240+youyi
butpos_x3=360+youyi
butpos_x4=480+youyi
butpos_x5=600+youyi
butpos_y=0

moshi = 0
cap = cv2.VideoCapture(0)
biaoding = 1

top=tk.Tk()
top.wm_title("功能展示")
top.geometry(str(window_width)+'x'+str(window_height))


def tkImage(frame):
   cvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
   pilImage=Image.fromarray(cvimage)
   pilImage = pilImage.resize((image_width, image_height),Image.ANTIALIAS)
   tkImage =  ImageTk.PhotoImage(image=pilImage)
   return tkImage


def button0():
    global moshi
    moshi = 0
def button1():
    global moshi
    moshi = 1
def button2():
    global moshi
    moshi = 2
def button3():
    global moshi
    moshi = 3
def button4():
    global moshi
    moshi = 4

def button5():
    _, frame=cap.read()
    img_name = './renlian/' + str(int(time.time())) + '.png'
    cv2.imwrite(img_name,frame)

#控件定义
canvas = tk.Canvas(top,bg='white',width=image_width,height=image_height)#绘制画布
b0=tk.Button(top,text='卡片识别',width=15,height=2,command=button0)
b1=tk.Button(top,text='人脸识别',width=15,height=2,command=button1)
b2=tk.Button(top,text='表情识别',width=15,height=2,command=button2)
b3=tk.Button(top,text='目标跟踪',width=15,height=2,command=button3)
b4=tk.Button(top,text='连续卡片识别',width=15,height=2,command=button4)
b5=tk.Button(top,text='保存图片',width=15,height=2,command=button5)
lb = tk.Listbox(top, width=30, height=27)

#控件位置设置
canvas.place(x=imagepos_x,y=imagepos_y)
b0.place(x=butpos_x0,y=butpos_y)
b1.place(x=butpos_x1,y=butpos_y)
b2.place(x=butpos_x2,y=butpos_y)
b3.place(x=butpos_x3,y=butpos_y)
b4.place(x=butpos_x4,y=butpos_y)
b5.place(x=butpos_x5,y=butpos_y)
lb.place(x=lb_x,y=lb_y)

if __name__=="__main__":
    
    while(True):
        # ref,frame=cap.read()
        frame=np.ones((100,100),np.uint8)
        img_t = frame.copy()
        picture = tkImage(img_t)
        if moshi == 0:
            kapianout, img_t = kapian_out(frame, 7, 15)
            picture = tkImage(img_t)
            if kapianout:
                lbi = '卡片:' + str(kapianout)
                lb.insert(0, lbi)
        if moshi == 1:
            renyuan, img_t = predictper(frame)
            picture = tkImage(img_t)
            if renyuan:
                lbi = '人物身份:' + str(renyuan)
                lb.insert(0, lbi)
        if moshi == 2:
            emotion_text, img_t = biaoqing(frame)
            picture = tkImage(img_t)
            if emotion_text:
                lbi = '表情:' + str(emotion_text)
                lb.insert(0, lbi)
        if moshi == 3:
            zx, zy, img_t = genzong(frame, biaoding)
            picture = tkImage(img_t)
            biaoding = 0
            if zx and zy:
                lbi = '中心坐标:({}, {})'.format(zx, zy)
                lb.insert(0, lbi)
        if moshi == 4:
            lianxu_out, img_t = lianxukapian(frame, 7, 15)
            picture = tkImage(img_t)
            if lianxu_out:
                lbi = '连续卡片:' + str(lianxu_out)
                lb.insert(0, lbi)

        canvas.create_image(0,0,anchor='nw',image=picture)
        top.update()
        top.after(40)

    top.mainloop()
    cap.release()