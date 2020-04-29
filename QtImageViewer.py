# encoding:utf8

import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.widget = QtImageViewer(self)
        self.widget.setGeometry(10, 10, 600, 600)
        self.setWindowTitle('Image with mouse control')
        self.widget.loadImageFromFile(r'D:\1.png')


class QtImageViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.img = QPixmap('./bg.jpg')
        #self.scaled_img = self.img.scaled(self.size(), Qt.KeepAspectRatio)
        self.scaled_img = self.scale(self.size())
        self.point = QPoint(0, 0)
        self.img_path = ''
        self.left_click = False

        self.initUI()

    def scale(self, *__args):
        return self.img.scaled(*__args, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def initUI(self):

        self.setWindowTitle('Image with mouse control')

    def paintEvent(self, e):
        '''
        绘图
        :param e:
        :return:
        '''
        painter = QPainter()
        painter.begin(self)
        self.draw_img(painter)
        painter.end()

    def draw_img(self, painter):
        painter.drawPixmap(self.point, self.scaled_img)

    def mouseMoveEvent(self, e):  # 重写移动事件
        if self.left_click:
            self._endPos = e.pos() - self._startPos
            self.point = self.point + self._endPos
            self._startPos = e.pos()
            self.repaint()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.left_click = True
            self._startPos = e.pos()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.left_click = False
        elif e.button() == Qt.RightButton:
            self.point = QPoint(0, 0)
            #self.scaled_img = self.img.scaled(self.size(), Qt.KeepAspectRatio)
            self.scaled_img = self.scale(self.size())
            self.repaint()

    def wheelEvent(self, e):
        scale_step = 25
        if e.angleDelta().y() < 0:
            # 放大图片
            #self.scaled_img = self.img.scaled(self.scaled_img.width()-scale_step, self.scaled_img.height()-scale_step, Qt.KeepAspectRatio)
            self.scaled_img = self.scale(self.scaled_img.width()-scale_step, self.scaled_img.height()-scale_step)
            new_w = e.x() - (self.scaled_img.width() * (e.x() - self.point.x())) / (self.scaled_img.width() + scale_step)
            new_h = e.y() - (self.scaled_img.height() * (e.y() - self.point.y())) / (self.scaled_img.height() + scale_step)
            self.point = QPoint(new_w, new_h)
            self.repaint()
        elif e.angleDelta().y() > 0:
            # 缩小图片
            #self.scaled_img = self.img.scaled(self.scaled_img.width()+scale_step, self.scaled_img.height()+scale_step, Qt.KeepAspectRatio)
            self.scaled_img = self.scale(self.scaled_img.width()+scale_step, self.scaled_img.height()+scale_step)
            new_w = e.x() - (self.scaled_img.width() * (e.x() - self.point.x())) / (self.scaled_img.width() - scale_step)
            new_h = e.y() - (self.scaled_img.height() * (e.y() - self.point.y())) / (self.scaled_img.height() - scale_step)
            self.point = QPoint(new_w, new_h)
            self.repaint()

    def resizeEvent(self, e):
        if self.parent is not None:
            #self.scaled_img = self.img.scaled(self.size(), Qt.KeepAspectRatio)
            self.scaled_img = self.scale(self.size())
            self.point = QPoint(0, 0)
            self.update()

    def loadImageFromFile(self, fileName=""):
        if len(fileName) == 0:
            fileName, dummy = QFileDialog.getOpenFileName(self, "Open image file.", directory='./tables')
        #if len(fileName) and os.path.isfile(fileName):
        #print(fileName)
        self.img_path = fileName
        self.img = QPixmap(fileName)
        #self.scaled_img = self.img.scaled(self.size(), Qt.KeepAspectRatio)
        self.scaled_img = self.scale(self.size())
        self.update()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    # ex = ImageWithMouseControl()

    ex.show()
    app.exec_()
