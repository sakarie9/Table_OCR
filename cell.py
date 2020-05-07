from utils import split_cell_coordinate
class Cell(object):
    """ Form에서 이루어지는 각각의 cell들의 대한 정보를 저장합니다.
     存储有关表单中每个单元格的信息"""

    def __init__(self):
        # 单元格矩阵
        # x,y为表格左上点坐标
        self.x = None
        self.y = None
        self.width = None
        self.height = None

        self.central_x = None
        self.central_y = None

        # 文字信息
        self.text = None
        self.text_height = None
        self.text_align = 'center'
        self.text_valign = 'vcenter'

        self.cell_name = None
        self.merged_info = None
        self.bg_color = '#ffffff'

        self.boundary = {
            'left': False,
            'right': False,
            'upper': False,
            'lower': False
        }

        self.need_del = False

    # ------------------------------------------------------------------------------------------------------------------
    def set_value(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.central_x = x + int(width / 2)
        self.central_y = y + int(height / 2)

    # ------------------------------------------------------------------------------------------------------------------
    def get_value(self):
        return self.x, self.y, self.width, self.height, self.central_x, self.central_y

    # ------------------------------------------------------------------------------------------------------------------
    def set_text(self, text, text_height, text_align, text_valign):
        self.text = text
        self.text_height = text_height
        self.text_align = text_align
        self.text_valign = text_valign

    # ------------------------------------------------------------------------------------------------------------------

    def get_cellname(self):
        return self.cell_name

    # ------------------------------------------------------------------------------------------------------------------
    def merge_horizontal(self, right_cell):
        """
        合并水平对齐的单元格
        :param right_cell：相对于当前单元格位于右侧的单元格
        """
        self.width += right_cell.width
        self.central_x = self.x + int(self.width / 2)
        self.boundary['right'] = right_cell.boundary['right']
        self.merged_info = right_cell.merged_info

    def merge_vertical(self, lower_cell):
        """
        合并水平对齐的单元格。
        :param lower_cell：相对于当前单元格位于底部的单元格
        """
        self.height += lower_cell.height
        self.central_y = self.y + int(self.height / 2)
        self.boundary['lower'] = lower_cell.boundary['lower']
        self.merged_info = lower_cell.merged_info

    def merge_to(self, br_cell):
        """
        从当前单元格起，合并到br_cell的所有单元格
        :param br_cell: 右下的任意单元格
        """
        self.width = br_cell.x + br_cell.width - self.x
        self.height = br_cell.y + br_cell.height - self.y
        self.central_x = self.x + int(self.width / 2)
        self.central_y = self.y + int(self.height / 2)
        self.boundary['right'] = br_cell.boundary['right']
        self.boundary['lower'] = br_cell.boundary['lower']
        self.merged_info = br_cell.merged_info

    # ------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        """
        使用控制台打印单元格的属性
        """
        s = str()
        s += 'x %d y %d\t|\t' % (self.x, self.y)
        s += 'w %d h %d\t|\t' % (self.width, self.height)

        s += self.cell_name + ':' + self.merged_info + '\t|\t'

        if self.text is not None:
            s += self.text
        else:
            s += 'None'

        s += '\t\theight: ' + str(self.text_height)
        s += '\talign/valign: ' + self.text_align + '/' + self.text_valign

        s += '\t\t'
        s += str(self.boundary)

        s += '\tneed_del：' + str(self.need_del)

        return s

    # ------------------------------------------------------------------------------------------------------------------
