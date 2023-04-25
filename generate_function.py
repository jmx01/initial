import copy
import random

import numpy as np
import pandas as pd

from initial_data import initial_data, standard_no_pick_zone


def is_continue(dt):
    """
    判断零件管是否用完
    :param dt: 零件管的镜像，一直在改变的值
    :return: 0或1
    """
    return np.where(dt[:, 1].max() != 0, 1, 0)


def MM_fetchOne(table, MaxOrMin="max", e=0.05, greedy=True):
    """
    默认table不为空
    最大或最小的一根  # 默认取最大的一根
    :param greedy: 判断是不是贪婪拿取
    :param e: 概率
    :param MaxOrMin: 标识符
    :param table: 原料或零件的镜像
    :return: 新的table和那根材料的名称数量和长度
    """
    table = np.array(table)
    quantity = table[:, 1]
    length = table[:, 2].copy()
    if greedy:
        pass
    else:
        if MaxOrMin == "max":
            if random.random() < e:
                MaxOrMin = "min"
            else:
                MaxOrMin = "max"
        elif MaxOrMin == "min":
            if random.random() >= e:
                MaxOrMin = "min"
            else:
                MaxOrMin = "max"

    if MaxOrMin == "max":  # 取最大的一根
        address = length.argmax()
        while quantity[address] == 0:
            length[address] = 0
            address = length.argmax()
    else:  # 取最小的一根
        address = length.argmin()
        while quantity[address] == 0:
            length[address] = 100000000
            address = length.argmin()

    fetch = table[address, :].copy()  # fetch为复制的table第i+1行的信息
    fetch[1] = 1  # 拿走的数量为1
    table[address, 1] -= 1  # 数量-1
    return table, fetch


def sequence_add(table, sequence):
    """对只有编码的序列添加长度"""
    table = pd.DataFrame(table, columns=["编号", "数量", "长度"])
    for i in range(len(sequence)):
        index = list(table["编号"]).index(sequence[i])
        add = list(table.iloc[index, [0, 2]])
        del sequence[i]
        sequence.insert(i, add)
    return sequence


def sequence_decode(sequence_M, sequence_P, no_pick_zone):
    """
    针对一个固定的零件管序列，原料管的解生成,未知有解
    :param no_pick_zone: 标准禁接区
    :param sequence_M: 输入的原材料序列，原材料用长度作为标识
    :param sequence_P: 零件序列，零件用名称作为标识，已知长度，格式为[编号，长度]
    :return: 解格式
    """
    solve = copy.deepcopy(sequence_M)  # 深复制［长度，剩余长度，[切割向量]，有效使用长度，剩余长度］
    change_zone = ["change", []]  # 创建一个整体的禁接区同禁接矩阵形式吻合
    cut_num = [0]  # 累积零件管长，最终为零件管总长
    cal_ma = [0, 0]  # 累积原料长度,左为上次终点，右为下次使用的点

    for i in range(len(sequence_P)):  # 对所有零件管
        name = sequence_P[i][0]  # 给出所有零件管的name str
        index = np.where(no_pick_zone[0] == name)  # 给出对应零件的禁接区

        for x in range(len(no_pick_zone[index, 1][0])):
            cut_num.append(cut_num[-1] + no_pick_zone[index, 1][0][x][0][0])
            for cc in range(len(no_pick_zone[index, 1][0][x])):
                change_zone[1].append(copy.deepcopy(no_pick_zone[index, 1][0][x][cc]))  # 将禁接区加到change_zone上

    change_zone, change_zone_cal = standard_no_pick_zone([change_zone])  # 生成变化后禁接区和累积禁接区
    change_zone_cal = change_zone_cal[0][1]

    return 0


data = initial_data()
