import cv2
import os
import numpy as np
import shutil
from string import ascii_uppercase


def rotate(image, angle, center=None, scale=1.0):
    (w, h) = image.shape[0:2]
    if center is None:
        center = (w // 2, h // 2)
    wrapMat = cv2.getRotationMatrix2D(center, angle, scale)
    return cv2.warpAffine(image, wrapMat, (h, w), borderValue=(255, 255, 255))


def del_files(path_to_folder):
    try:
        for file in os.listdir(path_to_folder):
            file_path = path_to_folder + os.sep + file
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                #os.removedirs(file_path)
                shutil.rmtree(file_path)
    except IOError:
        print('Delete Filed')


def get_dirs_3(path):
    list = path.split(os.sep, -1)
    d3 = list[-1].split('.')[0]
    d2 = list[-2]
    d1 = list[-3]
    return d1, d2, d3


def get_dirs_2(path):
    list = path.split(os.sep, -1)
    d2 = list[-1].split('.')[0]
    d1 = list[-2]
    return d1, d2


def add_white_space(img):
    additional_w = 20
    additional_h = 20
    WHITE = [255, 255, 255]
    img = cv2.copyMakeBorder(img, additional_h, additional_h, additional_w,
                             additional_w, cv2.BORDER_CONSTANT, value=WHITE)
    return img


'''水平投影'''
def getHProjection(image):
    hProjection = np.zeros(image.shape, np.uint8)
    # 图像高与宽
    (h, w) = image.shape
    # 长度与图像高度一致的数组
    h_ = [0] * h
    # 循环统计每一行白色像素的个数
    for y in range(h):
        for x in range(w):
            if image[y, x] == 255:
                h_[y] += 1
    # 绘制水平投影图像
    for y in range(h):
        for x in range(h_[y]):
            hProjection[y, x] = 255
    #cv2.imshow('hProjection2', hProjection)

    return h_


'''垂直投影'''
def getVProjection(image):
    vProjection = np.zeros(image.shape, np.uint8)
    # 图像高与宽
    (h, w) = image.shape
    # 长度与图像宽度一致的数组
    w_ = [0] * w
    # 循环统计每一列白色像素的个数
    for x in range(w):
        for y in range(h):
            if image[y, x] == 255:
                w_[x] += 1
    # 绘制垂直平投影图像
    for x in range(w):
        for y in range(h - w_[x], h):
            vProjection[y, x] = 255
    # cv2.imshow('vProjection',vProjection)
    return w_


def split_image(originImage, work_path, filename):
    """
    分割图片
    :param originImage: imread过的图片
    :param work_path: ocr的保存路径
    :param filename: 要分割的图片文件名
    :return:
    """
    filename = filename.split('.', -1)[0]
    image = cv2.cvtColor(originImage, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('gray', image)
    # 将图片二值化
    retval, img = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)
    # cv2.imshow('binary', img)

    kernel = np.ones((2, 2), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    # cv2.imshow('dilate', img)

    # 图像高与宽
    (h, w) = img.shape
    Position = []
    # 水平投影
    H = getHProjection(img)

    start = 0
    H_Start = []
    H_End = []
    # 根据水平投影获取垂直分割位置
    for i in range(len(H)):
        if H[i] > 0 and start == 0:
            H_Start.append(i)
            start = 1
        if H[i] <= 0 and start == 1:
            H_End.append(i)
            start = 0
    # if len(H_End) == 0:
    #     H_End.append(len(H))
    # 分割行，分割之后再进行列分割并保存分割位置
    for i in range(len(H_Start)):
        # 获取行图像
        cropImg = img[H_Start[i]:H_End[i], 0:w]
        # cv2.imshow('cropImg',cropImg)
        # 对行图像进行垂直投影
        W = getVProjection(cropImg)
        Wstart = 0
        Wend = 0
        W_Start = 0
        W_End = 0
        for j in range(len(W)):
            if W[j] > 0 and Wstart == 0:
                W_Start = j
                Wstart = 1
                Wend = 0
            if W[j] <= 0 and Wstart == 1:
                W_End = j
                Wstart = 0
                Wend = 1
            if Wend == 1:
                Position.append([W_Start, H_Start[i], W_End, H_End[i], i])
                Wend = 0

    temp = Position[0][4]
    j = 0
    # 根据确定的位置分割字符
    for m in range(len(Position)):
        #print(str(Position[m][4]), (Position[m][0], Position[m][1]), (Position[m][2], Position[m][3]))
        cropped = originImage[Position[m][1]:Position[m][3],
                  Position[m][0]:Position[m][2]]  # 裁剪坐标为[y0:y1, x0:x1]
        # cv2.imwrite('./temp/1/1/' + str(i) + '.' + str(m) + '.png', cropped)
        #cv2.imwrite(work_path + os.sep + filename + os.sep + str(i) + '.' + str(m) + '.png', cropped)

        if temp != Position[m][4]:
            temp = Position[m][4]
            j = 0

        path = work_path + os.sep + filename + os.sep + str(Position[m][4])
        if not os.path.exists(path):
            os.mkdir(path)
        cropped = add_white_space(cropped)
        cv2.imencode('.png', cropped)[1].tofile(path + os.sep + str(j) + '.png')
        j += 1
    if len(Position) == 0:
        # cv2.imwrite('./temp/1/1/' + '0' + '.' + '0' + '.png', originImage)
        #cv2.imwrite(work_path + os.sep + filename + os.sep + '0.0.png', originImage)

        path = work_path + os.sep + filename + os.sep + str(0)
        if not os.path.exists(path):
            os.mkdir(path)
        originImage = add_white_space(originImage)
        cv2.imencode('.png', originImage)[1].tofile(path + os.sep + str(0) + '.png')
    # cv2.imshow('image', originImage)


def split_image_col(originImage, work_path, filename):
    """
    分割图片
    :param originImage: imread过的图片
    :param work_path: ocr的保存路径
    :param filename: 要分割的图片文件名
    :return: 行数
    """
    ori_filename = filename
    filename = filename.split('.', -1)[0]
    image = cv2.cvtColor(originImage, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('gray', image)
    # 将图片二值化
    retval, img = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)
    # cv2.imshow('binary', img)

    kernel = np.ones((2, 2), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    # cv2.imshow('dilate', img)

    # 图像高与宽
    (h, w) = img.shape
    # 水平投影
    H = getHProjection(img)

    start = 0
    H_Start = []
    H_End = []
    # 根据水平投影获取垂直分割位置
    for i in range(len(H)):
        if H[i] > 0 and start == 0:
            H_Start.append(i)
            start = 1
        if H[i] <= 0 and start == 1:
            H_End.append(i)
            start = 0
    if len(H_Start) == len(H_End) == 1:
        shutil.copyfile(work_path+os.sep+ori_filename, work_path+os.sep+filename+os.sep+'0.png')
        return

    # 分割行，分割之后再进行列分割并保存分割位置
    for i in range(len(H_Start)):
        # 获取行图像
        cropped = originImage[H_Start[i]:H_End[i], 0:w]

        path = work_path + os.sep + filename
        cropped = add_white_space(cropped)
        cv2.imencode('.png', cropped)[1].tofile(path + os.sep + str(i) + '.png')


def get_temp_image_names():
    files = os.listdir('./temp')
    names = []
    for file in files:
        if file.find('.') != -1:  # 存在.
            names.append(file)
    #print(names)
    return names


def split_cell_coordinate(coor_str):
    coor_x = coor_str[0]
    coor_x = ord(coor_x) - ord('A')
    coor_y = coor_str[1:]
    coor_y = int(coor_y) - 1
    # print('coor_x:'+str(coor_x)+'\t'+'coor_y:'+str(coor_y))
    return coor_x, coor_y


def make_cell_coordinate(x, y):
    return ascii_uppercase[int(x)] + str(y+1)


def write_xml(path, filename, data_list):
    string = '<data>\n'
    for data in data_list:
        text1 = data[0]
        text2 = data[1]
        string = string + '\t<' + text1 + '>' + text2 + '</' + text1 + '>\n'
    string = string + '</data>'
    # print(path, filename, data_list)
    with open(path+filename+'.xml', "w") as f:
        f.write(string)
