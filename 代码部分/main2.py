import sys
from interface import Ui_MainWindow
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import shutil
import cv2
import time
import requests
from dazuiniao import kapian_out, predictper, biaoqing, genzong, lianxukapian
from urllib import request
from urllib import parse
import matplotlib
import numpy.core.multiarray
import matplotlib.backends.backend_tkagg
import _pywrap_tensorflow_internal

def showImage(label,image):
    height, width, bytesPerComponent = image.shape
    bytesPerLine = 3 * width
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    QImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
    pix = QPixmap.fromImage(QImg)
    label.setPixmap(pix)
    label.setScaledContents(True)

def restart_program():
  python = sys.executable
  os.execl(python, python, *sys.argv)

def isValid(ip):
    try:
        r = requests.get(ip, timeout=3)
        if r.status_code == 200:
            return True
        else:
            return False
    except:
        return False

def sendResult(var,val,addd='0'):
    params = {"var": var, "val": val, "addd": addd}
    url = "http://192.168.4.1/back"
    try:
        r = requests.get(url, params=params,timeout=0.5)
        return True
    except:
        print('无法访问远程服务器')
        return False

def getMode():
    url = "http://192.168.4.1/back"
    params = {"var": '0', "val": '0', "addd": '0'}
    try:
        r = requests.get(url, params=params,timeout=0.5)
    except:
        return None
    if r.status_code!=200:
        None
    else:
        if r.text!='':
            mode = int(r.text)
        else:
            mode=-1
    return mode

class Client():
    def __init__(self):
        os.system("cls")
        # init params
        self.personage_path= 'picture'
        self.process_mode=-1
        self.cap_index=0 #摄像头序号，本地，网络转本地，网络摄像头
        self.webcamera_url='http://192.168.4.1/capture'
        self.cap = cv2.VideoCapture(0)
        self.isAuto=False
        self.count=0

        self.app = QApplication(sys.argv)
        self.mainWindow = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.mainWindow)
        self.FormLoad()
        self.mainWindow.show()

        sys.exit(self.app.exec_())

    def FormLoad(self):
        self.loadPersonage()

        self.timer = QTimer(self.mainWindow)  # 初始化一个定时器
        self.timer.timeout.connect(self.time_Vis_out)  # 计时结束调用operate()方法
        self.timer.start(10)  # 设置计时间隔并启动

        self.ui.btn_creat.clicked.connect(self.btn_creat_click)
        self.ui.btn_delete.clicked.connect(self.btn_delete_click)
        self.ui.btn_save.clicked.connect(self.btn_save_click)

        self.ui.btn_kpsb.clicked.connect(self.btn_kpsb_click)
        self.ui.btn_rlsb.clicked.connect(self.btn_rlsb_click)
        self.ui.btn_bqsb.clicked.connect(self.btn_bqsb_click)
        self.ui.btn_mbgz.clicked.connect(self.btn_mbgz_click)
        self.ui.btn_lxkpsb.clicked.connect(self.btn_lxkpsb_click)
        self.ui.btn_changeCap.clicked.connect(self.btn_changeCap_click)
        self.ui.btn_auto.clicked.connect(self.btn_auto_click)
        self.ui.btn_restart.clicked.connect(self.btn_restart_click)
        self.ui.btn_kpgz.clicked.connect(self.btn_kpgz_click)


    #core function
    def time_Vis_out(self):
        try:
            if self.cap_index%3==2:
                self.cap=cv2.VideoCapture(self.webcamera_url)
                valid, self.frame = self.cap.read()
            else:
                valid, self.frame = self.cap.read()
            #get the frame,send to the algo
            if valid:
                if self.isAuto:self.auto_process()
                self.frame_res=self.process(self.frame)
                showImage(self.ui.Frame,self.frame_res)
            else:
                pass
        except Exception as e:
            print(e)
            print('happen a unknown error,please debug it!')
    def printMsg(self,msg):

        self.ui.list_msg.insertItem(0,msg)
        # self.ui.list_msg.addItem(msg)

        # if self.ui.list_msg.count()>1000:self.ui.list_msg.clear()
        # self.ui.list_msg.verticalScrollBar().setSliderPosition(self.ui.list_msg.verticalScrollBar().maximum()+1)

        # temp = self.ui.txt_msg.toPlainText()
        # self.ui.txt_msg.setText(msg+'\n')
        # self.ui.txt_msg.verticalScrollBar().setSliderPosition(self.ui.txt_msg.verticalScrollBar().maximum())

    def process(self,frame):
        res=frame
        if self.process_mode==0:
            out, res, _ = kapian_out(frame, 7, 15)
            if out:
                self.printMsg('卡片:'+str(out))
                sendResult('kpsb',out)
        elif self.process_mode==1:
            out, res = predictper(frame)
            if out:
                self.printMsg('人物身份:'+str(out))
                sendResult('rlsb', str(out))
        elif self.process_mode==2:
            out, res = biaoqing(frame)
            if out:
                self.printMsg('表情:'+str(out))
                sendResult('bqsb', out)
        elif self.process_mode==3:
            zx, zy, res = genzong(frame, self.baoding)
            # print('nihao123')
            if zx and zy:
                if self.count % 5 == 0:
                    self.printMsg('中心坐标:({}, {})'.format(zx, zy))
                self.count+=1
                sendResult('mbgz',str(zx),str(zy))
            # if not res:
            self.baoding=0
        elif self.process_mode==4:
            out, res = lianxukapian(frame, 7, 15)
            # print(out)
            if out:
                bli = '连续卡片:' + str(out)
                self.printMsg(bli)
                sendResult('lxkpsb', out)
        elif self.process_mode==5:
            out, res, (zx,zy) = kapian_out(frame, 7, 15,0)
            (zx,zy)=(int(zx),int(zy))
            if zx!=0 and zy!=0:
                if self.count % 5 == 0:
                    self.printMsg('卡片中心坐标:({}, {}):'.format(zx, zy))
                sendResult('kpgz', str(zx), str(zy))
                self.count+=1
        return res
    def btn_restart_click(self):
        QCoreApplication.instance().quit()
        self.mainWindow.hide()
        print('正在重启')
        restart_program()

    def btn_changeCap_click(self):
        self.cap_index+=1
        if self.cap_index%3==0:
            self.cap.release()
            self.cap = cv2.VideoCapture(0)
            self.printMsg('摄像头1')
        elif self.cap_index%3==1:
            self.cap.release()
            self.printMsg('摄像头2')
            self.cap = cv2.VideoCapture(1)
        elif self.cap_index%3==2:
            self.cap.release()
            self.printMsg('调用网络摄像头')
            if not isValid(self.webcamera_url):
                self.printMsg('无法打开网络摄像头，即将切换视频源')
                self.btn_changeCap_click()

    def btn_auto_click(self):
        hint = '关闭自动模式' if self.isAuto else '打开自动模式'
        self.isAuto=not self.isAuto
        self.ui.btn_auto.setDefault(not self.ui.btn_auto.isDefault())
        self.printMsg(hint)


    def auto_process(self):
        mode=getMode()
        if type(mode)==type(None):
            #failure to acess the target server,cancel auto process
            self.printMsg('无法访问远程服务器，将取消自动模式')
            self.btn_auto_click()
        else:
            if mode==self.process_mode:return #相同则返回，不做任何处理
            if mode==0:self.btn_kpsb_click()
            if mode==1:self.btn_rlsb_click()
            if mode==2:self.btn_bqsb_click()
            if mode==3:self.btn_mbgz_click()
            if mode==4:self.btn_lxkpsb_click()

    def btn_kpsb_click(self):
        self.process_mode=0
        self.printMsg('卡片识别')
    def btn_rlsb_click(self):
        self.process_mode = 1
        self.printMsg('人脸识别,当出现绿色框选时，可将人脸保存至对应人物中去。')
        print('人脸识别')
    def btn_bqsb_click(self):
        self.process_mode = 2
        self.printMsg('表情识别')
        print('表情识别')
    def btn_mbgz_click(self):
        self.process_mode = 3
        self.baoding=1
        self.printMsg('目标跟踪。在弹出框用鼠标选定目标，回车进行确认。')
        print('目标跟踪')
    def btn_lxkpsb_click(self):
        self.process_mode = 4
        self.printMsg('连续卡片识别')
        print('连续卡片识别')
    def btn_kpgz_click(self):
        self.process_mode = 5
        self.printMsg('卡片跟踪')

    def loadPersonage(self):
        self.personages = os.listdir('picture')
        self.ui.listObj.clear()
        self.ui.listObj.addItems(self.personages)
    def btn_creat_click(self):
        text, okPressed = QInputDialog.getText(self.mainWindow, "创建", "名称", QLineEdit.Normal, "")
        if okPressed and text != '':
            path=os.path.join(self.personage_path, text)
            if not os.path.exists(path):os.mkdir(path)
        self.loadPersonage()

    def btn_delete_click(self):
        index = self.ui.listObj.currentIndex().row()
        if index != -1:
            reply = QMessageBox.question(self.mainWindow, '警告', '是否删除')
            if reply == QMessageBox.Yes:
                self.currentObj = self.personages[index]
                print(self.currentObj)
                shutil.rmtree(os.path.join(self.personage_path, self.currentObj))
        self.loadPersonage()

    def btn_save_click(self):
        index = self.ui.listObj.currentIndex().row()
        if index != -1:
            self.currentObj = self.personages[index]
            name=os.path.join(self.personage_path, self.currentObj, str(int(time.time() * 100)) + '.jpg')
            cv2.imencode('.jpg', self.frame)[1].tofile(name)
            self.printMsg('成功保存至%s中'%(self.currentObj))
        else:
            self.printMsg('请选择保存的文件夹')

if __name__=="__main__":
    client = Client()
