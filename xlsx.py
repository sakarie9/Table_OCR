from ocr import OcrProcess
import xlsxwriter


class Export2XLSX(OcrProcess):
    def __init__(self, img_file, conf_file=None, verbose='vv', workbook='result.xlsx'):
        OcrProcess.__init__(self, img_file, conf_file=conf_file, verbose=verbose)
        # Create an new Excel file and add a worksheet.
        self.workbook = xlsxwriter.Workbook(workbook)

        self.default_format = dict()
        for key in self.config['xlsx_standard']['default_format']:
            self.default_format[key] = self.config['xlsx_standard']['default_format'][key]

        #self.export_to_xlsx()

    # ==========================================================================
    def export_to_xlsx(self):
        worksheet = self.workbook.add_worksheet()

        worksheet = self.make_base(worksheet)
        worksheet = self.merge_and_input_text(worksheet)

        self.workbook.close()

    # ==========================================================================
    def make_base(self, worksheet):
        """ 表格基本框架，例如单元格的高度和宽度
        :param worksheet: 工作表 worksheet
        :return: 返回 worksheet
        """
        #default_format = self.workbook.add_format(self.default_format)
        default_format = self.workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 13, 'bold': True})
        # 由于索引都是扭曲的，因此高度也会混乱，并且需要合并前的数据。
        for cols in range(0, len(self.before_merged)):
            worksheet.set_row(cols, self.before_merged[cols][0].height, default_format)  # height
            for rows in range(0, len(self.before_merged[cols])):
                present = self.before_merged[cols][rows]
                worksheet.set_column(rows, rows, present.width / 6.5, default_format)  # width/7
        return worksheet

    # ==========================================================================
    def merge_and_input_text(self, worksheet):
        """
        根据合并的信息合并单元格，并输入OCR读取的文本。
        如果当前单元格名称和merged_info名称相同，则表示该单元格尚未合并。
        如果不是，则表示该单元已合并。
        :param worksheet: 工作表 worksheet
        :return: 返回 worksheet
        """
        for cols in range(0, len(self.cells)):
            for rows in range(0, len(self.cells[cols])):
                present = self.cells[cols][rows]
                #cell_format = self.get_text_attribute(present)
                #cell_format.set_text_wrap()
                cell_format = self.workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter',
                                                        'font_size': 13, 'bold': True, 'text_wrap': True})
                # not merged
                if present.cell_name == present.merged_info:
                    if not present.text:
                        worksheet.write_blank(present.cell_name, None, cell_format)
                    else:
                        #worksheet.write_rich_string(present.cell_name, present.text, cell_format)
                        worksheet.write(present.cell_name, present.text, cell_format)
                # merged
                else:
                    worksheet.merge_range(present.cell_name + ':' + present.merged_info, None,
                                          cell_format=cell_format)
                    if not present.text:
                        worksheet.write_blank(present.cell_name, None, cell_format)
                    else:
                        #worksheet.write_rich_string(present.cell_name, present.text, cell_format)
                        worksheet.write(present.cell_name, present.text, cell_format)

        return worksheet

    # ==========================================================================
    def get_text_attribute(self, cell):
        boundary = cell.boundary
        top = 0
        bottom = 0
        left = 0
        right = 0
        if boundary['upper']:  # if boundary['upper'] == True
            top = 1  # 1 == Continuous line
        if boundary['lower']:
            bottom = 1
        if boundary['left']:
            left = 1
        if boundary['right']:
            right = 1
        cell_format = self.workbook.add_format({'font_name': 'Arial', 'font_color': '#000000',
                                                'align': cell.text_align, 'valign': cell.text_valign,
                                                'top': top, 'bottom': bottom, 'left': left, 'right': right,
                                                'font_size': cell.text_height, 'bg_color': cell.bg_color})
        return cell_format


