from preprocess import Preprocess
import pytesseract as ocr
import cv2
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor
import time
from multiprocessing import cpu_count
import utils


ocr_dir = os.path.abspath('.') + r'\temp\ocr'
ocr_dict = dict()  # A1:text
cellName_xy_dict = dict()  # A1:0,0
dict_texts = dict()


def multi_ocr(full_dir):
    text = ocr.image_to_string(full_dir, lang='chi_sim_simsun', config='--psm 7 -c preserve_interword_spaces=1')
    if not text:
        text = ocr.image_to_string(full_dir, lang='chi_sim', config='--psm 7 -c preserve_interword_spaces=1')
    d1, d2 = utils.get_dirs_2(full_dir)
    dict_texts[d1][int(d2)] = text
    #print(d1+' '+d2+' '+' '+text)
    return text


class OcrProcess(Preprocess):
    def __init__(self, img_file, conf_file=None, verbose='vv'):
        Preprocess.__init__(self, img_file, conf_file=conf_file, verbose=verbose)

        ocr_dict.clear()
        cellName_xy_dict.clear()
        dict_texts.clear()

        self.ocr_files = []

        if not os.path.exists(ocr_dir):
            os.mkdir(ocr_dir)
        else:
            utils.del_files(ocr_dir)
            #utils.del_dir_tree(ocr_dir)

        # self.process()
        # self.get_text_image()
        # self.split_process()
        # self.pre_ocr()
        # self.ocr_by_file()
        # self.fill_text()
        #
        # if self.verbose.startswith('vv'):
        #     self.cell_print()

    def fill_text(self):
        # merge
        for key, list1 in dict_texts.items():
            ocr_dict[key] = '\n'.join(list1)
        #print(ocr_dict)

        for key, value in ocr_dict.items():
            xy = cellName_xy_dict[key]
            x = str.split(xy)[0]
            y = str.split(xy)[1]
            self.cells[int(y)][int(x)].text = value
        #self.temp_print()

    def ocr_by_file(self):
        start = time.time()
        cpu = cpu_count()
        with ThreadPoolExecutor(cpu) as executor:
            executor.map(multi_ocr, self.ocr_files)
        end = time.time()

        if self.verbose.startswith('vv'):
            print("ocr time: " + str(end - start))
            #print(ocr_dict)
            #print(cellName_xy_dict)
            print(dict_texts)

    def get_text_image(self):
        for cols in range(len(self.cells)):
            for rows in range(len(self.cells[cols])):
                x, y, width, height, _, _ = self.cells[cols][rows].get_value()
                name = self.cells[cols][rows].get_cellname()
                # separated_img不超过原始图片
                if cols == 0 or rows == 0 or cols == len(self.cells) or rows == len(self.cells[cols]):
                    separated_img = self.erased_line[y:y + height, x:x + width]
                else:
                    separated_img = self.erased_line[y - 3:y + height + 3, x - 3:x + width + 3]

                img_for_calculate = self.get_processing_img(separated_img)
                # 在分离的图像中找到文本区域，计算高度，然后推断字体大小
                self.cells[cols][rows].text_height = self.get_text_height(img_for_calculate)

                # 在分离的图像中找到字符区域，然后推断align和valign
                self.cells[cols][rows].text_align, self.cells[cols][rows].text_valign \
                    = self.get_text_align(img_for_calculate)

                separated_img = self.erase_line_and_noise(separated_img)
                separated_img = self.del_blank(separated_img)

                if separated_img is not None:
                    separated_img = self.zoom_image(separated_img)
                    separated_img = self.add_white_space(separated_img)
                    #avg = np.mean(separated_img)
                    self._show_ocr_img(name, separated_img)
                    cellName_xy_dict[name] = str(rows) + ' ' + str(cols)
                    #text = ocr.image_to_string(separated_img, lang='chi_sim', config='psm 1')
                    #print(name+': '+text)

    def zoom_image(self, img):
        """
        为了提高OCR识别率，需要进行一些放大。
        可以在config.yaml中修改放大率。
        :param img：按单元格区域分隔的图像
        :return：返回放大的图像
        """
        zoom_fx = self.config['improve_ocr']['zoom_fx']
        zoom_fy = self.config['improve_ocr']['zoom_fy']

        img = cv2.resize(img, None, fx=zoom_fx, fy=zoom_fy, interpolation=cv2.INTER_CUBIC)

        return img

    def get_text_height(self, processed_img):
        """
        提取文本区域的轮廓以根据高度推断字体大小。
        10px == 7.5pt，大约是0.75倍。
        :param processing_img：处理后的图像以提取文本区域
        :return：如果找不到字符轮廓，返回默认字体大小
        """
        retrieve_mode = self.config['contour']['retrieve_mode']
        approx_method = self.config['contour']['approx_method']
        contours, _ = cv2.findContours(processed_img, retrieve_mode, approx_method)

        num = 0
        average_h = 0
        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)
            if (width > 10 and height > 10) and height < processed_img.shape[0] * 0.8:
                average_h += height
                num += 1
        if num:
            return int((average_h / num) * 0.75)  # 10px == 7.5pt
        else:
            return 11

    def get_text_align(self, processed_img):
        """
        推断单元格内文本的左右对齐以及上下对齐
        :param processing_img：处理后的图像以提取文本区域
        :return：推断的文本对齐方式
        """
        upper_blank, below_blank, left_blank, right_blank = self.detect_blank(processed_img)

        align = 'center'
        valign = 'vcenter'
        if max(upper_blank, below_blank) > min(upper_blank, below_blank) * 2:
            if min(upper_blank, below_blank) == upper_blank:
                valign = 'top'
            else:
                valign = 'bottom'
        if max(left_blank, right_blank) > min(left_blank, right_blank) * 2:
            if min(left_blank, right_blank) == left_blank:
                align = 'left'
            else:
                align = 'right'

        return align, valign

    def _show_ocr_img(self, title, target_img):
        temp_img = np.copy(target_img)
        #cv2.imwrite('./temp/result/ocr/' + title + '.png', temp_img)
        cv2.imencode('.png', temp_img)[1].tofile(ocr_dir + os.sep + title + '.png')

    def erase_line_and_noise(self, img):
        """
        使用HoughlineP方法删除长行，
        使用Canny边缘提取算法，除去图片中的噪音
        :param img：按单元格区域分隔的图像
        :return：去除了长线和噪点的图像
        """
        line_image = img * 0

        low_threshold = self.config['canny']['low_threshold']
        high_threshold = self.config['canny']['high_threshold']
        edges = cv2.Canny(img, low_threshold, high_threshold)

        rho = self.config['houghline']['rho']  # distance resolution in pixels of the Hough grid
        theta = np.pi / 180  # angular resolution in radians of the Hough grid
        threshold = self.config['houghline']['threshold']  # minimum number of votes (intersections in Hough grid Cell)
        min_line_length = min(img.shape[0], img.shape[1]) * 0.7  # minimum number of pixels making up a line
        max_line_gap = 0  # maximum gap in pixels between connectable line segments

        lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                                min_line_length, max_line_gap)
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 255), 2)

        kernel = np.ones((3, 3), np.uint8)
        closing = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=4)
        dilation = cv2.dilate(closing, kernel, iterations=2)

        img = cv2.addWeighted(img, 1, line_image, 1, 0)
        dilation = cv2.cvtColor(~dilation, cv2.COLOR_GRAY2BGR)

        img = cv2.addWeighted(img, 1, dilation, 1, 0)

        return img

    def detect_blank(self, processed_img):
        """
        返回基于文本区域的上，下，左和右页边距的大小。
        :param processing_img：处理后的图像以提取文本区域
        :return: 上，下，左和右页边距的大小
        """
        retrieve_mode = self.config['contour']['retrieve_mode']
        approx_method = self.config['contour']['approx_method']
        contours, hierarchy = cv2.findContours(processed_img, retrieve_mode, approx_method)

        origin_h = processed_img.shape[0]
        origin_w = processed_img.shape[1]

        upper_blank = 1000
        below_blank = 1000
        left_blank = 1000
        right_blank = 1000

        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)
            if width > 10 and height > 10:
                contour_upper = y
                contour_below = origin_h - (y + height)
                contour_left = x
                contour_right = origin_w - (x + width)

                if upper_blank > contour_upper:
                    upper_blank = contour_upper
                if below_blank > contour_below:
                    below_blank = contour_below
                if left_blank > contour_left:
                    left_blank = contour_left
                if right_blank > contour_right:
                    right_blank = contour_right

        return upper_blank, below_blank, left_blank, right_blank

    def del_blank(self, img):
        proc_img = self.get_processing_img(img)
        upper_blank, below_blank, left_blank, right_blank = self.detect_blank(proc_img)
        x0 = left_blank
        y0 = upper_blank
        x1 = len(img[0])-right_blank
        y1 = len(img)-below_blank
        if x0 == x1 or y0 == y1 or upper_blank == below_blank == left_blank == right_blank == 1000:
        #if upper_blank == below_blank == left_blank == right_blank == 1000:
            return None
        a = 0
        img = img[y0-a:y1+a, x0-a:x1+a]  # 裁剪坐标为[y0:y1, x0:x1]
        #img = img[y0:y1, x0:x1]
        return img

    def get_processing_img(self, img):
        """ 删除字符区域
        1) Gray-scale
        2) Canny edge
        3) GaussianBlur
        4) dilation
        5) opening
        :param img: 按单元格区域分隔的图片
        :return: processsed image
        """
        temp_img = img
        imgray = cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY)

        low_threshold = self.config['canny']['low_threshold']
        high_threshold = self.config['canny']['high_threshold']
        edges = cv2.Canny(imgray, low_threshold, high_threshold)

        blur = cv2.GaussianBlur(edges, (3, 3), 0)

        kernel = np.ones((3, 3), np.uint8)
        dilation = cv2.dilate(blur, kernel, iterations=1)

        opening = cv2.morphologyEx(dilation, cv2.MORPH_OPEN, kernel, iterations=2)
        return opening

    def add_white_space(self, img):
        """
        添加白边以提高OCR识别率。
        :param img：按单元格区域分隔的图片
        :return: 返回添加了边距的图像
        """

        additional_w = self.config['improve_ocr']['additional_width']
        additional_h = self.config['improve_ocr']['additional_height']

        WHITE = [255, 255, 255]
        img = cv2.copyMakeBorder(img, additional_h, additional_h, additional_w,
                                 additional_w, cv2.BORDER_CONSTANT, value=WHITE)
        return img

    def split_process(self):
        origin_files = os.listdir(ocr_dir)  # A1.png
        for i in range(len(origin_files)):  # 遍历所有ocr目录下的图片
            filename = origin_files[i]
            filename_woext = origin_files[i].split('.', -1)[0]
            full_path = ocr_dir+os.sep+filename
            if not os.path.exists(ocr_dir+os.sep+filename_woext):
                os.mkdir(ocr_dir+os.sep+filename_woext)
            #ori_img = cv2.imread(full_path)
            ori_img = cv2.imdecode(np.fromfile(full_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            #utils.split_image(ori_img, ocr_dir, filename)
            utils.split_image_col(ori_img, ocr_dir, filename)

    def pre_ocr(self):
        files = os.listdir(ocr_dir)
        dir_paths = []
        folders_1 = []
        # 向dict_texts中填充等量（待ocr图片数量）的空字符串
        for file in files:
            if file.find('.') == -1:  # 不存在.
                folders_1.append(file)
                dir_paths.append(ocr_dir + os.sep + file)
        # 遍历每个单元格文件夹
        for f_1 in folders_1:
            files = os.listdir(ocr_dir + os.sep + f_1)
            dict_texts[f_1] = (['']*len(files))
        # if self.verbose.startswith('vv'):
        #     print(dict_texts)

        # 添加所有待ocr文件(ocr_files
        g = os.walk(ocr_dir)
        for path, d, filelist in g:
            if ocr_dir == path:
                continue
            for filename in filelist:
                #print(os.path.join(path, filename))
                self.ocr_files.append(os.path.join(path, filename))
                #print(get_dirs(os.path.join(path, filename)))

    def __del__(self):
        global ocr_dict
        global cellName_xy_dict
        global dict_texts
        ocr_dict = dict()
        cellName_xy_dict = dict()
        dict_texts = dict()

    def ocr_process(self):
        self.process()
        self.get_text_image()
        self.split_process()
        self.pre_ocr()
        self.ocr_by_file()
        self.fill_text()

        # if self.verbose.startswith('vv'):
        #     self.cell_print()

