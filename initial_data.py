import numpy as np
import pandas as pd
import copy
import openpyxl


def primary_deal_npz(file):
    #有bug 禁接区长度不同，填充none
    wb = openpyxl.load_workbook(file)
    sheet = wb.active
    max_columns = sheet.max_column
    column = openpyxl.utils.get_column_letter(max_columns)

    all_list, each_list = [], []

    i = 1
    str1, str2 = 'A' + str(i), '%s' + str(i)

    while sheet[str1:str2 % column][0][0].value is not None:
        each_list.append(sheet[str1:str2 % column][0][0].value)
        each_list.append([])  # 一个空列表后续存禁接区长度和性质

        for j in range(len(sheet[str1:str2 % column][0]) - 1):
            length = sheet[str1:str2 % column][0][j + 1].value
            str1, str2 = 'A' + str(i + 1), '%s' + str(i + 1)
            pro = sheet[str1:str2 % column][0][j + 1].value
            str1, str2 = 'A' + str(i), '%s' + str(i)
            each_list[1].append([length, pro])

        all_list.append(each_list)

        i += 3
        str1, str2, each_list = 'A' + str(i), '%s' + str(i), []

    return all_list


def alpha_effect(table, al):
    for i in range(len(table)):
        for j in range(len(table[i][1])):
            window = table[i][1][j]
            if j not in [0, len(table[i][1]) - 1]:
                if window[1] == 1:
                    window[0] += 2 * al
                else:
                    window[0] -= 2 * al
            else:
                if window[1] == 1:
                    window[0] += al
                else:
                    window[0] -= al

    for i in range(len(table)):
        j = 0
        while j < len(table[i][1]) - 1:
            if table[i][1][j][0] < 0:
                if j != 0:
                    table[i][1][j][0] = table[i][1][j][0] + table[i][1][j + 1][0] + table[i][1][j - 1][0]
                    del table[i][1][j + 1], table[i][1][j - 1]
                    j -= 1
                else:
                    table[i][1][j][0] = table[i][1][j][0] + table[i][1][j + 1][0]
                    del table[i][1][j + 1]
            else:
                j += 1

    return table


def standard_no_pick_zone(table, al):
    """
    :aid 处理禁接区（标准化禁接区）
    :param al:
    :param table: 输入的原始的禁接矩阵
    :return: 处理好后的标准禁接矩阵
    """
    for i in range(len(table)):
        j = 0
        while j < len(table[i][1]) - 1:
            if table[i][1][j][1] == table[i][1][j + 1][1]:
                table[i][1][j][0] += table[i][1][j + 1][0]
                del table[i][1][j + 1]
            else:
                j += 1

    table = alpha_effect(table, al)
    zone = np.array(table, dtype=object)
    calculate_zone = copy.deepcopy(table)
    for i in range(len(table)):
        for j in range(len(table[i][1]) - 1):
            calculate_zone[i][1][j + 1][0] += calculate_zone[i][1][j][0]
    return zone, calculate_zone


def standard_data_input(table):
    table = table.groupby("长度").sum()  # 合并长度相同的行，index变为长度
    table["长度"] = table.index
    table.index = range(len(table["长度"]))  # 重新变为[编号，数量，长度]的形式
    return table


class initial_data(object):
    greedy_solution_quantity = 1  # 需要的贪婪解初始数，因为是纯贪婪，因此只用一个解
    random_solution_quantity = 63  # 随机解数
    over_time = 3600  # 初始解生成时间限制
    pick_up = 30  # 可放弃的新生成的原材料长度
    alpha = 0  # 建议离禁焊区的距离
    e = 0.05  # 概率随机取值
    datatable_input = 'data_input.xlsx'  # 输入文件的路径
    datatable_output = 'data_output.xlsx'  # 零件文件路径
    deal_no_pick_zone = 'zone.xlsx'  # 禁接区文件路径

    datatable_input = pd.read_excel(datatable_input)  # [编号、数量、长度]  输入材料
    datatable_output = pd.read_excel(datatable_output)  # [编号、数量、长度]  输出材料
    material_length = sum(np.array(datatable_input.iloc[:, 1]) * np.array(datatable_input.iloc[:, 2]))  # 输入材料总长度
    product_length = sum(np.array(datatable_output.iloc[:, 1]) * np.array(datatable_output.iloc[:, 2]))  # 输出材料总长度

    deal_no_pick_zone = primary_deal_npz(deal_no_pick_zone)  # 将文件处理为可处理的形式
    dt_input = standard_data_input(datatable_input)  #
    no_pick_zone, calculate_no_pick_zone = standard_no_pick_zone(deal_no_pick_zone, alpha)

    def __int__(self, greedy_solution_quantity, over_time, pick_up, alpha, e, material_length, product_length, dt_input,
                no_pick_zone, calculate_no_pick_zone):
        self.greedy_solution_quantity = greedy_solution_quantity
        self.over_time = over_time
        self.pick_up = pick_up
        self.alpha = alpha
        self.e = e
        self.material_length = material_length
        self.product_length = product_length
        self.dt_input = dt_input
        self.no_pick_zone = no_pick_zone
        self.calculate_no_pick_zone = calculate_no_pick_zone
