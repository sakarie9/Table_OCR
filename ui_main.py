import shutil
import sys
import os
import threading
import time

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QMainWindow, QDialog, QTableWidget, QHeaderView, \
    QAbstractItemView, QMenu, QFileDialog
from ui1 import Ui_MainWindow
from ui2 import Ui_Dialog as Tag_Dialog
from ui3 import Ui_Dialog as Batch_Dialog
import utils
from xlsx import Export2XLSX
from ocr import OcrProcess
from utils import split_cell_coordinate, make_cell_coordinate
from string import ascii_uppercase
import numpy as np

TAG_FILES_PATH = './tags/'
TAG_FILE_NAME = 'tag_list.txt'
TAG_FILE = TAG_FILES_PATH + TAG_FILE_NAME
CONFIG_FILE_PATH = './config.yaml'
OUTPUT_FILE_PATH = './output/'

cells: list
cols_count: int
rows_count: int

verbose = 'vv'


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.work: Export2XLSX
        self.names = []
        self.xlsx_name = ''
        self.image_path = ''

        self.setupUi(self)
        self.imageList.setVisible(False)

        self.status = 0

        if not os.path.exists(OUTPUT_FILE_PATH):
            os.mkdir(OUTPUT_FILE_PATH)

    # 自定义函数
    def loadImage(self):
        self.image1.loadImageFromFile()
        img_path = self.image1.img_path
        if img_path != '':
            self.image_path = img_path
            (filename, extension) = os.path.splitext(os.path.basename(img_path))
            self.xlsx_name = filename + '.xlsx'
            self.work = Export2XLSX(img_path, verbose=verbose, workbook=OUTPUT_FILE_PATH + self.xlsx_name)
            self.startProcess1()
            self.status = 1

    def reloadImage(self):
        if self.image_path != '':
            self.work = Export2XLSX(self.image_path, verbose=verbose, workbook=OUTPUT_FILE_PATH + self.xlsx_name)
            self.startProcess1()

    def changeImage(self):
        index = self.imageList.currentIndex()
        path = './temp/' + self.names[index]
        self.image2.loadImageFromFile(path)

    def startProcess1(self):
        self.work.process()

        self.names = utils.get_temp_image_names()
        self.imageList.clear()
        self.imageList.addItems(self.names)
        self.imageList.setVisible(True)
        self.imageList.setCurrentIndex(7)

    def editConfig(self):
        os.startfile(os.path.abspath(CONFIG_FILE_PATH))
        self.reloadImage()

    def startProcess2(self):
        if self.status == 0:
            QtWidgets.QMessageBox.information(self, '警告', '请先点击“打开图片”按钮！',
                                              QMessageBox.Close, QMessageBox.Close)
            return
        # self.startProcess1()

        start = time.time()
        self.reloadImage()
        self.work.ocr_process()
        self.work.export_to_xlsx()
        end = time.time()
        print("time: " + str(end - start))

        global cells
        global cols_count
        global rows_count
        cells = self.work.cells
        cols_count = len(self.work.final_x) - 1
        rows_count = len(self.work.final_y) - 1

        msgBox = QtWidgets.QMessageBox.information(self, '完成',
                                                   '耗时' + str(round((end - start), 2)) + 's\nExcel文件转换完成，是否打开？',
                                                   QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)
        if msgBox == QMessageBox.Ok:
            os.startfile(os.path.abspath(OUTPUT_FILE_PATH + self.xlsx_name))

        else:
            pass

        self.status = 2

    def openTagDialog(self):
        if self.status == 0:
            QtWidgets.QMessageBox.information(self, '警告', '请先点击“打开图片”按钮！',
                                              QMessageBox.Close, QMessageBox.Close)
            return
        elif self.status == 1:
            QtWidgets.QMessageBox.information(self, '警告', '请先点击“生成Excel”按钮！',
                                              QMessageBox.Close, QMessageBox.Close)
            return
        else:
            self.tag_dialog = MyTagDialog()
            self.tag_dialog.show()

    def openBatchDialog(self):
        self.batch_dialog = MyBatchDialog()
        self.batch_dialog.show()


class MyTagDialog(QDialog, Tag_Dialog):
    def __init__(self, is_batch=False):
        super(MyTagDialog, self).__init__()

        self.tag_status = 0
        self.tags_list = []

        if not os.path.exists(TAG_FILES_PATH):
            os.mkdir(TAG_FILES_PATH)

        self.setupUi(self)

        if not is_batch:
            # 允许右键产生菜单
            self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            # 将右键菜单绑定到槽函数generateMenu
            self.tableWidget.customContextMenuRequested.connect(self.generateMenu)

            self.make_base()
            self.fill_table()

    def batch_init(self):
        # 允许右键产生菜单
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # 将右键菜单绑定到槽函数generateMenu
        self.tableWidget.customContextMenuRequested.connect(self.generateMenu)

        self.make_base()
        self.fill_table()

    def make_base(self):
        # tableWidget
        self.tableWidget.setColumnCount(cols_count)
        self.tableWidget.setRowCount(rows_count)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header_list = []
        for i in range(cols_count):
            header_list.append(ascii_uppercase[i])
        self.tableWidget.setHorizontalHeaderLabels(header_list)

        # tableWidget_tags
        self.tableWidget_tags.setColumnCount(2)
        self.tableWidget_tags.setRowCount(0)
        self.tableWidget_tags.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_tags.setHorizontalHeaderLabels(['Tag', 'Data'])
        self.tableWidget_tags.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget_tags.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 读取文件
        self.load_tags()

    def fill_table(self):
        for y in range(len(cells)):
            for x in range(len(cells[y])):
                present = cells[y][x]
                coor_x, coor_y = split_cell_coordinate(present.cell_name)
                text = present.text
                if text is not None:
                    pass
                    # text = text.replace('\n', ' ')
                self.tableWidget.setItem(coor_y, coor_x, QTableWidgetItem(text))
                if present.cell_name != present.merged_info:
                    coor_x2, coor_y2 = split_cell_coordinate(present.merged_info)
                    self.tableWidget.setSpan(coor_y, coor_x, coor_y2 - coor_y + 1, coor_x2 - coor_x + 1)

    def generateMenu(self, pos):
        qtcell = self.tableWidget.selectionModel().selection().indexes()[0]
        row_num = qtcell.row()
        col_num = qtcell.column()
        menu = QMenu()
        item1 = menu.addAction(u'选择标签')
        item2 = menu.addAction(u'选择数据')
        action = menu.exec_(self.tableWidget.mapToGlobal(pos))
        # 显示选中行的数据文本
        if action == item1:
            self.tag_status = 1
            self.tags_list.clear()
            text = self.tableWidget.item(row_num, col_num).text()
            coor = make_cell_coordinate(col_num, row_num)
            self.tags_list.append(coor)
            # print('你选了选项一，当前行文字内容是：', text)
        if action == item2 and self.tag_status == 1:
            self.tag_status = 2
            text = self.tableWidget.item(row_num, col_num).text()
            coor = make_cell_coordinate(col_num, row_num)
            self.tags_list.append(coor)
            # print('你选了选项二，当前行文字内容是：', text)
            # 填表
            current_row = self.tableWidget_tags.rowCount()
            self.tableWidget_tags.setRowCount(self.tableWidget_tags.rowCount() + 1)
            self.tableWidget_tags.setItem(current_row, 0, QTableWidgetItem(self.tags_list[0]))
            self.tableWidget_tags.setItem(current_row, 1, QTableWidgetItem(self.tags_list[1]))
            self.save_tags()  # 随时保存

    def save_tags(self):
        tags_list_save = []
        for y in range(self.tableWidget_tags.rowCount()):
            temp_list = [self.tableWidget_tags.item(y, 0).text(), self.tableWidget_tags.item(y, 1).text()]
            tags_list_save.append(temp_list)
        numpy_list = np.asarray(tags_list_save)
        np.savetxt(TAG_FILE, numpy_list, fmt='%s', delimiter=' ')  # 这样就以文本的形式把刚才的数组保存下来了

    def load_tags(self):

        if not os.path.exists(TAG_FILE) or os.path.getsize(TAG_FILE) == 0:
            return

        # tags_list_save = np.loadtxt(TAGS_FILE_PATH)
        tags_list_save = np.loadtxt(TAG_FILE, dtype=bytes).astype(str)
        # print(tags_list_save.shape)
        if tags_list_save.ndim == 1:
            tags_list_save = [tags_list_save]
        # print(tags_list_save)

        self.tableWidget_tags.setRowCount(0)
        self.tableWidget_tags.clearContents()

        for i in range(len(tags_list_save)):
            item = tags_list_save[i]
            row = self.tableWidget_tags.rowCount()
            self.tableWidget_tags.insertRow(row)
            for j in range(len(item)):
                item = QTableWidgetItem(str(tags_list_save[i][j]))
                self.tableWidget_tags.setItem(row, j, item)

    # 按钮相关函数
    def deleteRow(self):
        current_row = self.tableWidget_tags.currentRow()
        self.tableWidget_tags.removeRow(current_row)
        self.save_tags()

    def clearTable(self):
        self.tableWidget_tags.setRowCount(0)
        self.tableWidget_tags.clearContents()
        self.save_tags()

    def output(self):
        for y in range(self.tableWidget_tags.rowCount()):
            coor_x, coor_y = split_cell_coordinate(self.tableWidget_tags.item(y, 0).text())
            text1 = self.tableWidget.item(coor_y, coor_x).text()
            # text1 = text1.strip().replace(' ', '').replace('\n', '')
            text1 = text1.strip().replace('\n', '')
            coor_x, coor_y = split_cell_coordinate(self.tableWidget_tags.item(y, 1).text())
            text2 = self.tableWidget.item(coor_y, coor_x).text()
            # text2 = text2.strip().replace(' ', '').replace('\n', '')
            text2 = text2.strip().replace('\n', '')
            print('<' + text1 + '>' + text2 + '<' + text1 + '/>')

    def load(self):
        fileName, dummy = QFileDialog.getOpenFileName(self, "打开保存的标签", TAG_FILES_PATH, "Text Files (*.txt)")
        if fileName == '':
            QtWidgets.QMessageBox.information(self, '警告', '无效文件！',
                                              QMessageBox.Close, QMessageBox.Close)
        else:
            try:
                shutil.copyfile(fileName, TAG_FILE)
            except shutil.SameFileError:
                pass
            self.load_tags()

    def save(self):
        fileName, dummy = QFileDialog.getSaveFileName(self, "保存标签", TAG_FILES_PATH, "Text Files (*.txt)")
        if fileName == '':
            QtWidgets.QMessageBox.information(self, '警告', '无效文件！',
                                              QMessageBox.Close, QMessageBox.Close)
        else:
            try:
                shutil.copyfile(TAG_FILE, fileName)
            except shutil.SameFileError:
                pass


class MyBatchDialog(QDialog, Batch_Dialog):
    def __init__(self):
        super(MyBatchDialog, self).__init__()
        self.setupUi(self)

        self.path = None
        self.mode = None
        self.is_path_ok = False
        self.is_tag_ok = False
        self.is_processing = False
        self.is_stop = False

        self.MyTagDialog = MyTagDialog(is_batch=True)

    def get_radio_select(self):
        name = self.buttonGroup.checkedButton().objectName()
        if name == 'radioButton1':
            self.mode = 1
        elif name == 'radioButton2':
            self.mode = 2
        elif name == 'radioButton3':
            self.mode = 3
        else:
            self.mode = 1
        return self.mode

    def set_progress(self, now_value, max_value):
        self.progressBar.setMaximum(max_value)
        self.progressBar.setValue(now_value)
        self.label.setText(str(now_value) + '/' + str(max_value))

    def selectFolder(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "getExistingDirectory", "./")
        is_have_pics = False
        names = os.listdir(directory)
        for name in names:
            if name.endswith('.jpg') or name.endswith('.png'):
                is_have_pics = True
        if directory is not None and is_have_pics:
            self.path = directory
            self.is_path_ok = True
        else:
            self.is_path_ok = False

    def selectTag(self):
        self.MyTagDialog.load()
        self.is_tag_ok = True

    def startProcess(self):
        t = threading.Thread(target=self.startProcess1, name="Process1")
        t.start()

    def startProcess1(self):
        self.startButton.setEnabled(False)
        self.get_radio_select()
        self.is_stop = False

        pics = os.listdir(self.path)
        list_pics = []
        for pic in pics:
            if pic.endswith('.jpg') or pic.endswith('.png'):
                list_pics.append(self.path + os.sep + pic)

        global cells
        global cols_count
        global rows_count

        # self.progressBar.setMaximum(len(list_pics))
        # self.label.setText('0/' + str(len(list_pics)))
        self.set_progress(0, len(list_pics))

        for i, pic in enumerate(list_pics):
            if self.is_stop:
                self.is_stop = False
                return
            if self.mode == 1:
                (filename, extension) = os.path.splitext(os.path.basename(pic))
                xlsx_name = filename + '.xlsx'
                work = Export2XLSX(pic, verbose=verbose, workbook=OUTPUT_FILE_PATH + xlsx_name)
                work.ocr_process()
                work.export_to_xlsx()

                cells = work.cells
                cols_count = len(work.final_x) - 1
                rows_count = len(work.final_y) - 1

                self.MyTagDialog.batch_init()
                self.MyTagDialog.output()

            elif self.mode == 2:
                (filename, extension) = os.path.splitext(os.path.basename(pic))
                xlsx_name = filename + '.xlsx'
                work = Export2XLSX(pic, verbose=verbose, workbook=OUTPUT_FILE_PATH + xlsx_name)
                work.ocr_process()
                work.export_to_xlsx()
            elif self.mode == 3:
                work = OcrProcess(pic, verbose=verbose)
                work.ocr_process()

                cells = work.cells
                cols_count = len(work.final_x) - 1
                rows_count = len(work.final_y) - 1

                self.MyTagDialog.batch_init()
                self.MyTagDialog.output()

            # self.progressBar.setValue(i + 1)
            # self.label.setText(str(i + 1) + '/' + str(len(list_pics)))
            self.set_progress(i + 1, len(list_pics))

        self.startButton.setEnabled(True)
        self.label.setText('完成！')

    def cancelProcess(self):
        self.is_stop = True
        self.startButton.setEnabled(True)
        pass


def start_ui():
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
