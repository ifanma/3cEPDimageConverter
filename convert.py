import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from PyQt5.QtGui import QImage, QPixmap, qRgb, QIntValidator
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QGridLayout,
                             QLabel, QPushButton, QSlider, QLineEdit)
from PyQt5.QtCore import Qt
from functools import partial

# 不错的参数：black:203, red:158, white:86

class win(QDialog):
    def __init__(self):

        # 初始化一个img的ndarray, 用于存储图像
        self.width = 212
        self.height = 104

        self.black_thred = 128
        self.red_thred = 128
        self.white_thred = 128

        self.img_input = np.array(np.zeros((self.height, self.width, 3), dtype='uint8'))
        self.img_output = np.array(())
        self.img_black = np.array(())
        self.img_red = np.array(())
        self.img_white = np.array(())
        self.img_ver = np.array(())

        self.img_black_show = np.array(())
        self.img_red_show = np.array(())
        self.img_white_show = np.array(())
        self.img_ver_show = np.array(())

        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(400, 300)
        self.btnOpen = QPushButton('Open', self)
        self.btnSave = QPushButton('Save', self)
        self.btnProcess = QPushButton('Process', self)
        self.btnQuit = QPushButton('Quit', self)
        self.btnOpen.setAutoDefault(False)
        self.btnSave.setAutoDefault(False)
        self.btnProcess.setAutoDefault(False)
        self.btnQuit.setAutoDefault(False)

        self.label_input = QLabel()
        self.label_output = QLabel()
        self.label_black = QLabel()
        self.label_red = QLabel()
        self.label_white = QLabel()
        self.label_ver = QLabel()

        self.label_input_text = QLabel()
        self.label_output_text = QLabel()
        self.label_black_text = QLabel()
        self.label_red_text = QLabel()
        self.label_white_text = QLabel()
        self.label_ver_text = QLabel()

        self.label_black_slider = QSlider(Qt.Horizontal)
        self.label_red_slider = QSlider(Qt.Horizontal)
        self.label_white_slider = QSlider(Qt.Horizontal)

        self.width_linedit = QLineEdit(str(self.width))
        self.width_linedit.setValidator(QIntValidator()) 
        self.width_linedit.setMaxLength(4)
        self.height_linedit = QLineEdit(str(self.height))
        self.height_linedit.setValidator(QIntValidator())
        self.height_linedit.setMaxLength(4)

        # 布局设定
        layout = QGridLayout(self)
        layout.addWidget(self.label_input, 0, 0, 3, 4)
        layout.addWidget(self.label_black, 0, 4, 3, 4)
        layout.addWidget(self.label_white, 0, 8, 3, 4)
        layout.addWidget(self.label_output, 4, 0, 3, 4)
        layout.addWidget(self.label_red, 4, 4, 3, 4)
        layout.addWidget(self.label_ver, 4, 8, 3, 4)

        layout.addWidget(QLabel('输入图片'), 3, 0, 1, 1)
        layout.addWidget(QLabel('黑色部分'), 3, 4, 1, 1)
        layout.addWidget(QLabel('白色部分'), 3, 8, 1, 1)
        layout.addWidget(QLabel('输出图片'), 7, 0, 1, 1)
        layout.addWidget(QLabel('红色部分'), 7, 4, 1, 1)
        layout.addWidget(QLabel('校验'), 7, 8, 1, 1)

        layout.addWidget(self.label_black_slider, 3, 5, 1, 2)
        layout.addWidget(self.label_white_slider, 3, 9, 1, 2)
        layout.addWidget(self.label_red_slider, 7, 5, 1, 2)

        layout.addWidget(self.btnOpen, 8, 0, 1, 1)
        layout.addWidget(self.btnSave, 8, 1, 1, 1)
        layout.addWidget(self.btnProcess, 8, 4, 1, 1)
        layout.addWidget(self.btnQuit, 8, 5, 1, 1)

        layout.addWidget(self.width_linedit, 8, 8, 1, 1)
        layout.addWidget(self.height_linedit, 8, 9, 1, 1)

        # 默认值
        self.label_black_slider.setMaximum(255)
        self.label_black_slider.setMinimum(0)
        self.label_black_slider.setValue(128)
        self.label_black_slider.setSingleStep(1)

        self.label_red_slider.setMaximum(255)
        self.label_red_slider.setMinimum(0)
        self.label_red_slider.setValue(128)
        self.label_red_slider.setSingleStep(1)

        self.label_white_slider.setMaximum(255)
        self.label_white_slider.setMinimum(0)
        self.label_white_slider.setValue(128)
        self.label_white_slider.setSingleStep(1)
        
        self.label_black_slider.valueChanged.connect(self.sliderValuechange)
        self.label_black_slider.sliderPressed.connect(partial(self.sliderPre, 1))
        self.label_red_slider.valueChanged.connect(self.sliderValuechange)
        self.label_red_slider.sliderPressed.connect(partial(self.sliderPre, 2))
        self.label_white_slider.valueChanged.connect(self.sliderValuechange)
        self.label_white_slider.sliderPressed.connect(partial(self.sliderPre, 3))

        # 信号与槽连接, PyQt5与Qt5相同, 信号可绑定普通成员函数
        self.btnOpen.clicked.connect(self.openSlot)
        self.btnSave.clicked.connect(self.saveSlot)
        self.btnProcess.clicked.connect(self.processSlot)
        self.btnQuit.clicked.connect(self.close)

        self.width_linedit.returnPressed.connect(self.widthChanged)
        self.height_linedit.returnPressed.connect(self.heightChanged)

        self.processSlot()


    def openSlot(self):
        # 调用打开文件diglog
        fileName, tmp = QFileDialog.getOpenFileName(
            self, 'Open Image', './include/', '*.png *.jpg *.bmp')

        if fileName == '':
            return

        # 采用opencv函数读取数据
        img_read = cv2.imread(fileName)

        if img_read.size == 1:
            return
        
        self.img_input = img_read
        
        self.processSlot()
        self.refreshShow()

    def saveSlot(self):
        # 调用存储文件dialog
        fileName, tmp = QFileDialog.getSaveFileName(
            self, 'Save Array', './include/images.h', '*.h *.txt')

        if fileName == '':
            return
        if self.img_input.size == 1:
            return
        if self.img_black.size == 1:
            return
        if self.img_red.size == 1:
            return

        # 把c数组数据存入头文件中
        data_invert = 1
        os.remove(fileName)
        with open(fileName, 'w+') as f:
            # write black image to images.h
            total_size = np.int32(np.floor(self.img_black.shape[0]/8) * self.img_black.shape[1])
            print(f'const unsigned char gImage_black[{total_size}] = {{ /* 0X01,0X01,0XD4,0X00,0X63,0X00, */', file=f)
            for i in range(self.img_black.shape[1]):
                print_cnt = 0
                data = np.uint8(0)
                for j in range(self.img_black.shape[0]):
                    data |= (self.img_black[j, i] ^ data_invert) << (7 - print_cnt)
                    print_cnt += 1
                    if print_cnt == 8:
                        print_cnt = 0
                        print('0x%02x,'%data, file=f, end='')
                        data = np.uint8(0)
                if print_cnt != 0:
                    print('0x%02x,'%data, file=f, end='')
                print('', file=f, end='\n')

            print('};\n\n', file=f)

            # write red image to images.h
            total_size = int(self.img_red.shape[0]/8) * self.img_red.shape[1]
            total_size = np.int32(np.floor(self.img_red.shape[0]/8) * self.img_red.shape[1])
            print(f'const unsigned char gImage_red[{total_size}] = {{ /* 0X01,0X01,0XD4,0X00,0X63,0X00, */', file=f)
            for i in range(self.img_red.shape[1]):
                print_cnt = 0
                data = np.uint8(0)
                for j in range(self.img_red.shape[0]):
                    data |= (self.img_red[j, i] ^ data_invert) <<  (7 - print_cnt)
                    print_cnt += 1
                    if print_cnt == 8:
                        print_cnt = 0
                        print('0x%02x,'%data, file=f, end='')
                        data = np.uint8(0)
                if print_cnt != 0:
                    print('0x%02x,'%data, file=f, end='')
                print('', file=f, end='\n')

            print('};\n\n', file=f)


    def processSlot(self):
        if self.img_input.size == 1:
            return
        
        # print(self.img_input.shape[0], self.img_input.shape[1])
        if self.img_input.shape[1] / self.img_input.shape[0] > self.width / self.height:
            img = cv2.resize(self.img_input, (int(self.width), int(self.img_input.shape[0] / self.img_input.shape[1] * self.width)))
        elif self.img_input.shape[1] / self.img_input.shape[0] < self.width / self.height:
            img = cv2.resize(self.img_input, (int(self.img_input.shape[1] / self.img_input.shape[0] * self.height), int(self.height)))
        else:
            img = self.img_input

        pad_w = self.width - img.shape[1] 
        pad_h = self.height - img.shape[0] 
        top,bottom = pad_h//2, pad_h-(pad_h//2)
        left,right = pad_w//2, pad_w -(pad_w//2)
        self.img_pre = cv2.copyMakeBorder(img,top,bottom,left,right,cv2.BORDER_CONSTANT,None,(255,255,255)) 

        # print(self.img_pre.shape[0], self.img_pre.shape[1])
        
        self.img_black = np.array(((self.img_pre[:, :, 0]<self.black_thred) & (self.img_pre[:, :, 1] < self.black_thred) & (self.img_pre[:, :, 2] < self.black_thred)), dtype='int8')
        self.img_white = np.array(((self.img_pre[:, :, 0]>self.white_thred) & (self.img_pre[:, :, 1] > self.white_thred) & (self.img_pre[:, :, 2] > self.white_thred)), dtype='int8')
        self.img_red = np.abs(np.array((self.img_pre[:, :, 2]>self.red_thred), dtype='int8')  - self.img_white)
        self.img_ver = self.img_black | self.img_white| self.img_red

        self.img_output = self.img_pre.copy()
        for i in range(self.img_output.shape[0]):
            for j in range(self.img_output.shape[1]):
                if self.img_red[i, j]:      # 红色好像是后渲染的，会把黑色覆盖掉，而不是反过来
                    self.img_output[i, j] = [255., 0, 0]
                elif self.img_black[i, j]:
                    self.img_output[i, j] = [0., 0., 0.]
                else:
                    self.img_output[i, j] = [255., 255., 255.]

        # 定义颜色映射
        colors = np.array([[68, 1, 84], [253, 231, 37]])

        # 使用向量化操作来创建不同颜色主题的图像展示
        self.img_black_show = np.array(colors[self.img_black], dtype='uint8')  # 假设 self.img_black 是一个与 self.img_input 形状相同的布尔型数组
        self.img_white_show = np.array(colors[self.img_white], dtype='uint8')
        self.img_red_show = np.array(colors[self.img_red], dtype='uint8')
        self.img_ver_show = np.array(colors[self.img_ver], dtype='uint8')

        # titles = ['img','black','white','red', 'result', 'ver']
        # img = cv2.cvtColor(self.img_input, cv2.COLOR_BGR2RGB)
        # images = [img,self.img_black, self.img_white, self.img_red, self.img_output, self.img_ver]
        # for i in range(6):
        #     plt.subplot(2,3,i+1),plt.imshow(images[i])
        #     plt.title(titles[i])
        #     plt.xticks([]),plt.yticks([])
        # # plt.show()

        self.refreshShow()

    def refreshShow(self):
        # 提取图像的尺寸和通道, 用于将opencv下的image转换成Qimage
        # height, width, channel = self.img_input.shape
        qImg_input = QImage(self.img_input.data, self.img_input.shape[1], self.img_input.shape[0], 3 * self.img_input.shape[1],
                           QImage.Format_RGB888).rgbSwapped()
        self.label_input.setPixmap(QPixmap.fromImage(qImg_input))           # 将Qimage显示出来

        qImg_output = QImage(self.img_output.data, self.img_output.shape[1], self.img_output.shape[0], 3 * self.img_output.shape[1],
                           QImage.Format_RGB888)
        self.label_output.setPixmap(QPixmap.fromImage(qImg_output))           # 将Qimage显示出来
        
        qImg_black = QImage(self.img_black_show.data, self.img_black_show.shape[1], self.img_black_show.shape[0], 3*self.img_black_show.shape[1],
                             QImage.Format_RGB888)
        self.label_black.setPixmap(QPixmap.fromImage(qImg_black))           # 将Qimage显示出来
        
        qImg_red = QImage(self.img_red_show.data, self.img_red_show.shape[1], self.img_red_show.shape[0], 3 * self.img_red_show.shape[1],
                           QImage.Format_RGB888)
        self.label_red.setPixmap(QPixmap.fromImage(qImg_red))           # 将Qimage显示出来
        
        qImg_white = QImage(self.img_white_show.data, self.img_white_show.shape[1], self.img_white_show.shape[0], 3 * self.img_white_show.shape[1], 
                            QImage.Format_RGB888)
        self.label_white.setPixmap(QPixmap.fromImage(qImg_white))           # 将Qimage显示出来
        
        qImg_ver = QImage(self.img_ver_show.data, self.img_ver_show.shape[1], self.img_ver_show.shape[0], 3 *self.img_ver_show.shape[1],
                           QImage.Format_RGB888)
        self.label_ver.setPixmap(QPixmap.fromImage(qImg_ver))           # 将Qimage显示出来


    def sliderValuechange(self):
        self.black_thred = self.label_black_slider.value()
        self.red_thred = self.label_red_slider.value()
        self.white_thred = self.label_white_slider.value()
        print(f'black:{self.black_thred}, red:{self.red_thred}, white:{self.white_thred}')
        self.processSlot()

    def sliderPre(self, index):
        if index == 1:
            self.black_thred = 128
            self.label_black_slider.setValue(128)
        if index == 2:
            self.red_thred = 128
            self.label_red_slider.setValue(128)
        if index == 3:
            self.white_thred = 128
            self.label_white_slider.setValue(128)

    def widthChanged(self):
        if self.width_linedit.text() !='' and int(self.width_linedit.text()) > 64:
            self.width = int(self.width_linedit.text())
            self.processSlot()

    def heightChanged(self):
        if self.height_linedit.text() !='' and int(self.height_linedit.text()) > 64:
            self.height = int(self.height_linedit.text())
            self.processSlot()



if __name__ == '__main__':
    a = QApplication(sys.argv)
    w = win()
    w.show()
    sys.exit(a.exec_())


