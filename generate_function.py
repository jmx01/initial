import numpy as np
import pandas as pd
import random
import copy
from initial_data import initial_data, standard_no_pick_zone


def e_rule(string, e):
    return np.where(string == "max", np.where(random.random() < e, "min", string),
                    np.where(random.random() < e, "max", string))


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
        MaxOrMin = e_rule(MaxOrMin, e)

    if MaxOrMin == "max":  # 取最大的一根
        address = length.argmax()
        while quantity[address] == 0:
            length[address] = 0
            address = length.argmax()
    else:  # 取最小的一根
        address = length.argmin()
        while quantity[address] == 0:
            length[address] = 1000000
            address = length.argmin()

    fetch = table[address, :].copy()  # fetch为复制的table第i+1行的信息
    fetch[1] = 1  # 拿走的数量为1
    table[address, 1] -= 1  # 数量-1
    return table, fetch


def change_solution(GS_new, string):
    if string == "meng":
        GM = copy.deepcopy(GS_new)
        meng_1, meng_2, meng_3 = [[0], []], [0], []
        ma_in = pd.DataFrame(GM[0]).iloc[:, [0, 2]]

        # 计算 坐标，长度
        ma = np.array(ma_in).tolist()
        ma.insert(0, [0, [0]])
        for i in range(ma_in.shape[0]):
            ma[i + 1][0] = ma[i + 1][0] + ma[i][0]

        for i in range(ma_in.shape[0]):
            for j in ma[i + 1][1]:
                meng_1[0].append(j + ma[i][0])
        meng_1[0].pop()
        for i in range(len(meng_1[0])):
            meng_1[1].append(GM[1][i][1])

        # 计算 触发禁忌的管材
        ma.pop(0)
        ma_in = pd.DataFrame(GM[0])
        ma = np.array(ma_in).tolist()
        for i in ma:
            np.where(i[4] > 0, i.append(1), i.append(0))
            i.append(len(i[2]))

        for i in range(ma_in.shape[0] - 1):
            ma[i + 1][6] = ma[i + 1][6] + ma[i][6]
            if ma[i + 1][5] == 1:
                meng_2.append(ma[i + 1][6] + 1)

        GS = [meng_1, meng_2, meng_3]
        return GS
    elif string == "yuan":
        GY = copy.deepcopy(GS_new)
        ma_in = copy.deepcopy(GY[0])
        GC = []

        for i in ma_in:
            i.append(len(i[2]))
        for i in range(len(ma_in) - 1):
            ma_in[i + 1][5] = ma_in[i + 1][5] + ma_in[i][5]
        ma_in.insert(0, [0, 0, [0], 0, 0, 0])
        po = GY[1]
        for i in range(len(ma_in) - 1):
            each = []
            last_count = ma_in[i][5]  # 上一根原料到的根数。
            for j in range(len(ma_in[i + 1][2])):
                if ma_in[i + 1][2][j] == po[last_count + j][1]:
                    each.append([1, last_count + j, po[last_count + j][1]])
                else:
                    each.append([2, last_count + j, ma_in[i + 1][2][j]])
            if ma_in[i + 1][3] != 0:
                each.append([2, ma_in[i + 1][5], ma_in[i + 1][3]])
            each.append([0, ma_in[i + 1][4]])
            GC.append(each)

        return GC


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
    针对一个固定的零件管序列，原料管的解生成
    :param no_pick_zone: 标准禁接区
    :param sequence_M: 输入的原材料序列，原材料用长度作为标识
    :param sequence_P: 零件序列，零件用名称作为标识，已知长度，格式为[编号，长度]
    :return: 解格式
    """
    solve = copy.deepcopy(sequence_M)
    change_zone = ["change", []]
    cut_point = []  # 累积切割点
    cut_num = 0  # 累积零件管长，最终为零件管总长
    cal_ma = 0  # 累积原料长度

    for i in range(len(sequence_P)):
        name = sequence_P[i][0]
        index = np.where(no_pick_zone[0] == name)
        change_zone[1].extend(no_pick_zone[index][1])
        cut_num += no_pick_zone[index][1]
        cut_point.append(cut_num)

    change_zone = [change_zone]
    change_zone, change_zone_cal = standard_no_pick_zone(change_zone)  # 生成变化后禁接区和累积禁接区
    change_zone_cal = change_zone_cal[1]

    return solve


data = initial_data()
