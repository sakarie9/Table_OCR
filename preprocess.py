import os
import cv2
import yaml
import numpy as np
import math
import utils
from cell import Cell
from string import ascii_uppercase
import sys


class Preprocess(object):
    def __init__(self, img_file, conf_file=None, verbose='v'):
        if img_file:
            if not os.path.exists(img_file):
                raise IOError('Cannot find image file "%s"' % img_file)
        self.img_file = img_file
        #self.img = cv2.imread(img_file)
        self.img = cv2.imdecode(np.fromfile(img_file, dtype=np.uint8), cv2.IMREAD_COLOR)

        # self.Origin_image = cv2.imread(img_file)
        self.Origin_image = self.img.copy()
        self.line_image = self.img * 0  # 表格线图
        self.erased_line = None  # 表格去线图
        self.closing_line = None

        # 原图的长宽
        self.origin_height, self.origin_width = self.Origin_image.shape[:2]

        if not conf_file:
            # 默认读取当前程序包位置中的config.yaml文件
            conf_file = '%s/config.yaml' \
                        % os.path.abspath(os.path.dirname(__file__))
            if not os.path.exists(conf_file):
                raise IOError('Cannot find config file "%s"' % conf_file)
        self.config_str = None
        self.config = self._read_config(conf_file)

        # 必要的行和列的列表
        self.final_x = None
        self.final_y = None

        # 提取单元之间的最小宽度和高度
        self.find_min_width = None
        self.find_min_height = None

        # 单元格信息
        self.cells = None
        self.before_merged = None

        self.verbose = verbose

    def _read_config(self, config_file):
        """
        从yaml文件读取配置
        :param config_file:
        :return: 返回配置的字典
        """
        # read contents from .yam config file
        with open(config_file, 'r', encoding='UTF-8') as ifp:
            self.config_str = ifp.read()
        with open(config_file, 'r', encoding='UTF-8') as ifp:
            # return yaml.load(ifp)
            return yaml.safe_load(ifp)

    def _show_img(self, title, target_img):
        temp_img = np.copy(target_img)
        #if self.verbose.startswith('vv'):
            # if self.origin_width > 1000 or self.origin_height > 1000:
            #    temp_img = cv2.resize(temp_img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            # cv2.imshow(title, temp_img)
            # cv2.waitKey(0)
            #cv2.imwrite('./temp/' + title + '.png', temp_img)
        cv2.imwrite('./temp/' + title + '.png', temp_img)

    def _get_threshold(self, imgray, mode):
        low_threshold = self.config[mode]['low_threshold']
        high_threshold = self.config[mode]['high_threshold']
        thr_type = self.config[mode]['thr_type']

        ret, thr = cv2.threshold(imgray, low_threshold, high_threshold, thr_type)
        # th2 = cv2.adaptiveThreshold(imgray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 2)
        # th3 = cv2.adaptiveThreshold(imgray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)
        return thr

    def cell_print(self):
        """
        cell's info printing method for debugging
        """
        if self.verbose.startswith('vv'):
            imgt = np.zeros((self.origin_height, self.origin_width, 3), np.uint8)
            imgt.fill(255)
            for cols in range(len(self.cells)):
                for rows in range(len(self.cells[cols])):
                    cellt = self.cells[cols][rows]
                    print(cellt)
                    x, y, width, height, central_x, central_y = cellt.get_value()
                    cv2.rectangle(imgt, (x, y), (x + width, y + height), (255, 0, 0), thickness=3)
                    cv2.putText(imgt, cellt.get_cellname(), (central_x, central_y), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
            self._show_img("9_cells", imgt)

    # ------------------------------------------------------------------------------------------------------------------

    def rotation_correction(self):
        # 灰度转换
        gray_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        # 腐蚀、膨胀
        kernel = np.ones((5, 5), np.uint8)
        erode_Img = cv2.erode(gray_img, kernel)
        eroDil = cv2.dilate(erode_Img, kernel)
        # cv2.imwrite("./temp/eroDil.png", eroDil)
        # 边缘检测
        canny = cv2.Canny(eroDil, 50, 150)
        # canny = Preprocessing(eroDil).sobel()
        # cv2.imwrite("./temp/canny.png", canny)
        # 霍夫变换得到线条
        lines = cv2.HoughLinesP(canny, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
        drawing = np.zeros(self.img.shape[:], dtype=np.uint8)
        # 画出线条
        biglength = 0
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(drawing, (x1, y1), (x2, y2), (0, 255, 0), 1, lineType=cv2.LINE_AA)
            # 计算曼哈顿距离，求出最长直线
            mlength = np.sum(np.abs(np.array([x1, y1]) - np.array([x2, y2])))
            if biglength < mlength:
                biglength = mlength
                # 获取最长直线对应的点坐标
                mx1, my1, mx2, my2 = x1, y1, x2, y2

        # cv2.imwrite("./temp/houghP.png", drawing)
        """
        计算角度,因为x轴向右，y轴向下，所有计算的斜率是常规下斜率的相反数，我们就用这个斜率（旋转角度）进行旋转
        """
        if mx1 == mx2:
            k = 0
        else:
            k = float(my1 - my2) / (mx1 - mx2)

        thera = np.degrees(math.atan(k))

        """
        旋转角度大于0，则逆时针旋转，否则顺时针旋转
        """
        rotateImg = utils.rotate(self.img, thera)
        # cv2.drawContours(rotateImg, np.array([[[mx1, my1]], [[mx2, my2]]]), -1, (0, 255, 0), 20)

        # 进行左右多余白边的裁剪
        lines = np.squeeze(lines)
        # 最小x
        min_x = sys.maxsize
        for line in lines:
            min_x = min(min_x, line[0])
        # 最大x
        max_x = 0
        for line in lines:
            max_x = max(max_x, line[2])
        cropped = rotateImg[0:len(rotateImg)-1, min_x:max_x]  # 裁剪坐标为[y0:y1, x0:x1]

        self.img = cropped.copy()
        self.Origin_image = cropped.copy()
        self.origin_height, self.origin_width = self.Origin_image.shape[:2]
        self._show_img("1_rotate_img", self.img)
        if self.verbose.startswith('vv'):
            print('旋转角度：'+str(thera))

    # ------------------------------------------------------------------------------------------------------------------

    def boxing_ambiguous(self):
        """
        在图像中，仅向上或向下应用线，或者未绘制边框，并且单元格以颜色为边框
        强制将边框与模糊的边框相对。
        """
        imgray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        mode = 'boxing'
        thr = self._get_threshold(imgray, mode)

        min_width = self.config['contour']['min_width']
        min_height = self.config['contour']['min_height']
        retrieve_mode = self.config['contour']['retrieve_mode']
        approx_method = self.config['contour']['approx_method']
        contours, hierarchy = cv2.findContours(thr, retrieve_mode, approx_method)

        i = 0
        # 第一次轮廓检测，使边框更清晰
        for contour in contours:
            # 左上坐标 宽 高
            x, y, width, height = cv2.boundingRect(contour)

            # 临近像素bgr中值
            mid_b = 0
            mid_g = 0
            mid_r = 0
            j = 0
            for my in range(y - 2, y + 3):
                for mx in range(x - 2, x + 3):
                    if (my and mx) >= 0 and (my < self.img.shape[0]) and (mx < self.img.shape[1]):
                        mid_b += int(self.img.item(my, mx, 0))  # b
                        mid_g += int(self.img.item(my, mx, 1))  # g
                        mid_r += int(self.img.item(my, mx, 2))  # r
                        j += 1
            mid_b = (mid_b / j) * 0.7  # strengthen darkness
            mid_g = (mid_g / j) * 0.7
            mid_r = (mid_r / j) * 0.7

            # Draw rectangle with median bgr
            # larger than the half of original image size
            if width > self.origin_width * 0.5 or height > self.origin_height * 0.5:
                self.img = cv2.rectangle(self.img, (x + 1, y + 1), (x + width - 1, y + height - 1),
                                         (mid_b, mid_g, mid_r, 50), 2)
                # self.img = cv2.rectangle(self.img, (x + 1, y + 1), (x + width - 1, y + height - 1),
                #                          (0, 255, 0, 50), 2)
                i += 1
                continue
            if (width > min_width and height > min_height) and ((hierarchy[0, i, 2] != -1 or hierarchy[0, i, 3] == (
                    len(hierarchy) - 2 or len(hierarchy) - 1)) or cv2.arcLength(contour, True) > 1000):
                # 轮廓不带子级（最外层）或父级，最外层或最外层-1
                # 或弧长> 1000以上
                self.img = cv2.rectangle(self.img, (x - 1, y - 1), (x + width + 1, y + height + 1),
                                         (mid_b, mid_g, mid_r, 50), 2)
                # self.img = cv2.rectangle(self.img, (x - 1, y - 1), (x + width + 1, y + height + 1),
                #                          (255, 0, 0, 50), 2)
            i += 1
        self._show_img('2_strengthen_img', self.img)

    # ------------------------------------------------------------------------------------------------------------------

    def detect_contours(self):
        """
        使用腐蚀膨胀获取line_image
        """
        gray_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        scale = self.config['detect']['scale']

        # 自适应阈值(对灰度图取反
        threshold_img = cv2.adaptiveThreshold(~gray_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -5)

        # 横向
        horizontal_img = threshold_img.copy()
        # 取图片的横向长
        horizontal_size = int(horizontal_img.shape[1] / scale)
        # 构建形态学因子
        h_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
        # 腐蚀 膨胀
        h_erode = cv2.erode(horizontal_img, h_structure, 1)
        h_dilate = cv2.dilate(h_erode, h_structure, 1)
        # cv2.imwrite("./temp/erodil_h.png", h_dilate)

        # 纵向
        vertical_img = threshold_img.copy()
        # 取图片的横向长
        vertical_size = int(vertical_img.shape[0] / scale)
        # 构建形态学因子
        v_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))
        # 腐蚀 膨胀
        v_erode = cv2.erode(vertical_img, v_structure, 1)
        v_dilate = cv2.dilate(v_erode, v_structure, 1)
        # cv2.imwrite("./temp/erodil_v.png", v_dilate)

        # 直线图
        lines_img = h_dilate + v_dilate
        self.line_image = cv2.cvtColor(lines_img, cv2.COLOR_GRAY2BGR)
        # cv2.imwrite("./temp/lines.png", lines_img)
        self._show_img('3_line_img', self.line_image)

    # ------------------------------------------------------------------------------------------------------------------

    def morph_closing(self):
        """
        在Line_image中，使用Morph Close填充线和线之间存在的空隙
        由于线与线之间存在的空间是实际线所在的空间，因此在计算时没有必要。
        """
        kernel_row = self.config['closing']['kernel_size_row']
        kernel_col = self.config['closing']['kernel_size_col']
        kernel = np.ones((kernel_row, kernel_col), np.uint8)

        closing_iter = self.config['closing']['iteration']

        self.closing_line = cv2.morphologyEx(self.line_image, cv2.MORPH_CLOSE, kernel, iterations=closing_iter)

        self._show_img('4_closing_line_img', self.closing_line)

    # ------------------------------------------------------------------------------------------------------------------

    def erase_line(self):
        """
        用Line_image覆盖Original_imgae以消除边框
        """
        # image that will be erased with white color
        # self.closing_line = cv2.cvtColor(self.closing_line, cv2.COLOR_GRAY2BGR)
        self.erased_line = cv2.addWeighted(self.Origin_image, 1, self.closing_line, 1, 0)
        self._show_img('5_erased_img', self.erased_line)

    # ------------------------------------------------------------------------------------------------------------------

    def draw_axis(self):
        tmp_img1 = np.copy(self.line_image)
        tmp_img2 = np.copy(self.erased_line)

        for x in self.final_x:
            cv2.line(tmp_img1, (x, 0), (x, self.origin_height), (0, 0, 255), 2)
        for y in self.final_y:
            cv2.line(tmp_img1, (0, y), (self.origin_width, y), (0, 255, 0), 2)
        self._show_img('6_draw_axis1', tmp_img1)

        for x in self.final_x:
            cv2.line(tmp_img2, (x, 0), (x, self.origin_height), (0, 0, 255), 2)
        for y in self.final_y:
            cv2.line(tmp_img2, (0, y), (self.origin_width, y), (0, 255, 0), 2)
        self._show_img('7_draw_axis2', tmp_img2)

    def approx_axis(self, needed_axis, find_min_axis, axis='x'):
        """
        压缩列表的值以有效获取所需的轴数。
        :param needed_axis：从cal_cell_needed方法获得的必需x或y轴的列表
        :param find_min_axis: 用于压缩x，y轴列表的阈值
        :param axis: x或y
        :return：压缩的x，y轴列表
        """
        final_axis = set()
        temp_int = needed_axis[0]
        num_temp_int = 1
        for a in range(1, len(needed_axis)):
            if needed_axis[a] - needed_axis[a - 1] < find_min_axis:
                temp_int += needed_axis[a]
                num_temp_int += 1
            else:
                final_axis.add(int(temp_int / num_temp_int))
                num_temp_int = 1
                temp_int = needed_axis[a]
        final_axis.add(int(temp_int / num_temp_int))
        # todo:暂时去掉最边上的框
        # if min(final_axis) > find_min_axis:
        #     final_axis.add(0)
        # if self.origin_width - max(final_axis) > find_min_axis:
        #     if axis == 'x':
        #         final_axis.add(self.origin_width)
        #     elif axis == 'y':
        #         final_axis.add(self.origin_height)

        final_axis = sorted(list(final_axis))
        return final_axis

    def cal_cell_needed(self):
        """
        在封闭的line_image上再次应用cv2.findContour()，以计算所需的x，y轴。
        """
        imgray = cv2.cvtColor(self.closing_line, cv2.COLOR_BGR2GRAY)

        mode = 'default_threshold'
        thr = self._get_threshold(imgray, mode)

        min_width = self.config['contour']['min_width']
        min_height = self.config['contour']['min_height']
        retrieve_mode = self.config['contour']['retrieve_mode']
        approx_method = self.config['contour']['approx_method']
        contours, hierarchy = cv2.findContours(thr, retrieve_mode, approx_method)

        needed_x = []
        needed_y = []
        find_min_width = self.config['num_of_needed_cell']['find_min_width']
        find_min_height = self.config['num_of_needed_cell']['find_min_height']

        for contour in contours:
            # 左上坐标 宽 高
            x, y, width, height = cv2.boundingRect(contour)
            if find_min_width > width and width > min_width:
                find_min_width = width
            if find_min_height > height and height > min_height:
                find_min_height = height

            if width > min_width or height > min_height:
                # self.line_image = cv2.rectangle(self.line_image, (x, y), (x + width, y + height), (255, 0, 0, 50), 2)
                needed_x.append(x)
                needed_x.append(x + width)
                needed_y.append(y)
                needed_y.append(y + height)

        # 所需单元格的个数
        needed_x = sorted(list(set(needed_x)))  # list(set(my_list)) --> 重复数据删除
        needed_y = sorted(list(set(needed_y)))

        self.find_min_width = find_min_width
        self.find_min_height = find_min_height

        # 轮廓与轮廓之间的线无用
        # 根据最小轮廓矩形的宽度和高度压缩相似的值
        self.final_x = self.approx_axis(needed_x, int(find_min_width * 0.5), 'x')
        self.final_y = self.approx_axis(needed_y, int(find_min_height * 0.5), 'y')

        self.draw_axis()

    # ------------------------------------------------------------------------------------------------------------------

    def save_cell_value(self):
        """
        到目前为止提取的每个单元格的x，y，宽度和高度值
        在每个单元格中输入一个由字母数字字符组成的名称，以使使用Excel更加方便。
        """
        self.cells = [[Cell() for rows in range(len(self.final_x) - 1)] for cols in
                      range(len(self.final_y) - 1)]
        self.before_merged = [[Cell() for rows in range(len(self.final_x) - 1)] for cols in
                              range(len(self.final_y) - 1)]

        for cols in range(len(self.final_y) - 1):
            for rows in range(len(self.final_x) - 1):
                x = self.final_x[rows]
                y = self.final_y[cols]
                width = self.final_x[rows + 1] - self.final_x[rows]
                height = self.final_y[cols + 1] - self.final_y[cols]

                self.cells[cols][rows].set_value(x, y, width, height)
                self.before_merged[cols][rows].set_value(x, y, width, height)

                self.cells[cols][rows].cell_name = ascii_uppercase[rows] + "%d" % (cols + 1)
                # 如果cell_name和merged_info相同，则不会合并
                self.cells[cols][rows].merged_info = ascii_uppercase[rows] + "%d" % (cols + 1)
                self.before_merged[cols][rows].cell_name = ascii_uppercase[rows] + "%d" % (cols + 1)

    # ------------------------------------------------------------------------------------------------------------------

    def find_cell_boundary(self):
        """
        基于line_image，确定每个单元格的中心坐标上，下，左或右是否有白色（b，g，r = 255）值。
        如果存在白色值，则确定存在边界。
        """
        for cols in range(len(self.final_y) - 1):
            for rows in range(len(self.final_x) - 1):
                x, y, width, height, central_x, central_y = self.cells[cols][rows].get_value()
                if rows == 0:
                    self.cells[cols][rows].boundary['left'] = True  # 第一竖列
                if rows == len(self.final_x) - 1:
                    self.cells[cols][rows].boundary['right'] = True  # 最后一竖列
                if cols == 0:
                    self.cells[cols][rows].boundary['upper'] = True  # 第一横列
                if cols == len(self.final_y) - 1:
                    self.cells[cols][rows].boundary['lower'] = True  # 最后一横列

                # 'white'的 b != 0
                for left in range(x + 1, central_x):
                    if self.line_image.item(central_y, left, 0) != 0:
                        self.cells[cols][rows].boundary['left'] = True
                        break
                for right in range(x + width - 1, central_x, -1):
                    if self.line_image.item(central_y, right, 0) != 0:
                        self.cells[cols][rows].boundary['right'] = True
                        break
                for upper in range(y + 1, central_y):
                    if self.line_image.item(upper, central_x, 0) != 0:
                        self.cells[cols][rows].boundary['upper'] = True
                        break
                for lower in range(y + height - 1, central_y, -1):
                    if self.line_image.item(lower, central_x, 0) != 0:
                        self.cells[cols][rows].boundary['lower'] = True
                        break

        #self.temp_print()

    # ------------------------------------------------------------------------------------------------------------------

    def is_have_boundary_right(self, row, col):
        y = row
        x = col
        if x == len(self.cells[y]) - 1:
            return True
        else:
            now_cell = self.cells[y][x]
            right_cell = self.cells[y][x + 1]
            if now_cell.boundary['right'] or right_cell.boundary['left']:
                return True
            return False

    def is_have_boundary_lower(self, row, col):
        y = row
        x = col
        if y == len(self.cells) - 1:
            return True
        else:
            now_cell = self.cells[y][x]
            lower_cell = self.cells[y + 1][x]
            if now_cell.boundary['lower'] or lower_cell.boundary['upper']:
                return True
            return False

    def set_flag_del(self, x1, y1, x2, y2):
        """
        将从(y1, x1)到(y2, x2)的单元格全部标记为需要删除(need_del)
        (y1, x1)除外
        """
        for y in range(y1, y2+1):  # 遍历y1到y2
            for x in range(x1, x2+1):
                cell = self.cells[y][x]
                cell.need_del = True
        self.cells[y1][x1].need_del = False

    def merge(self):
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                now = self.cells[y][x]
                br_x = None
                br_y = None
                # 如果是要删除的单元格，跳过
                if now.need_del:
                    continue
                # 如果不需要合并，跳过
                if now.boundary['right'] == True and now.boundary['lower'] == True:
                    continue
                # 横向遍历
                for tmp_x in range(x, len(self.cells[y])):
                    tmp_cell = self.cells[y][tmp_x]
                    # 如果右边无边界
                    # if tmp_cell.boundary['right'] == False:
                    if self.is_have_boundary_right(y, tmp_x) == False:
                        # del self.cells[y][tmp_x]
                        # 如果这不是第一个单元格则删除
                        ###if x != tmp_x:
                        ###    self.cells[y][tmp_x].need_del = True
                        continue
                    # 如果右边有边界
                    else:
                        # 确定x
                        br_x = tmp_x
                        # 如果下边有边界
                        # if tmp_cell.boundary['lower']:
                        if self.is_have_boundary_lower(y, tmp_x):
                            # 确定y，结束本次横向遍历
                            br_y = y
                            break
                        # 如果下边无边界
                        else:
                            # 开始纵向遍历
                            for tmp_y in range(y, len(self.cells)):
                                tmp_cell = self.cells[tmp_y][br_x]
                                # 下面有边界则确定y
                                # if tmp_cell.boundary['lower']:
                                if self.is_have_boundary_lower(tmp_y, br_x):
                                    br_y = tmp_y
                                    # 结束纵向遍历
                                    break
                                # 下面无边界
                                ###else:
                                    # del self.cells[tmp_y][br_x]
                                    # 不是第一个单元格则删除
                                    ###if tmp_y != y or br_x != x:
                                    ###    self.cells[tmp_y][br_x].need_del = True
                                # 检查下一个下面的左边界是否存在
                                # tmp_cell = self.cells[tmp_y+1][br_x]
                                # tmp_cell_l = self.cells[tmp_y+1][br_x-1]
                                # if tmp_cell.boundary['left'] or tmp_cell_l.boundary['right']:
                                #     br_y = tmp_y
                                #     break

                            # 结束横向遍历
                            break
                # 若待合并格与合并格是一个则continue
                # break会导致后面的格子处理不到
                if br_x == x and br_y == y:
                    continue
                now.merge_to(self.cells[br_y][br_x])
                self.set_flag_del(x, y, br_x, br_y)
                # del self.cells[br_y][br_x]
                ###self.cells[br_y][br_x].need_del = True

    def clean_merge(self):
        ys = len(self.cells)
        for y in range(ys):
            xs = len(self.cells[y])
            x_flag = 0
            for x in range(xs):
                x -= x_flag

                now_cell = self.cells[y][x]

                if now_cell.need_del:
                    del self.cells[y][x]
                    x_flag += 1
                    xs -= 1
                else:
                    continue

    def merge_cell(self):
        # self.merge_cell_horizontal()
        # self.merge_cell_vertical()
        self.merge()
        self.clean_merge()

        tmp_img = np.copy(self.erased_line)

        cols_range = len(self.cells)
        for cols in range(cols_range):
            rows_range = len(self.cells[cols])
            for rows in range(rows_range):
                x, y, width, height, _, _ = self.cells[cols][rows].get_value()
                cv2.rectangle(tmp_img, (x, y), (x + width, y + height),
                              (255, 0, 0, 50), 2)

        self._show_img('8_cell_merged', tmp_img)
        #self.temp_print()

    # ------------------------------------------------------------------------------------------------------------------

    def process(self):
        self.rotation_correction()
        self.boxing_ambiguous()
        self.detect_contours()
        self.morph_closing()
        self.erase_line()
        self.cal_cell_needed()
        self.save_cell_value()
        self.find_cell_boundary()
        self.merge_cell()
