import numpy as np
import pandas as pd
import random
import copy


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


def sequence_decryption(sequence_M, sequence_P):
    """
    用来对一个序列解密，生成解
    :param sequence_M: 输入的原材料序列，原材料用长度作为标识
    :param sequence_P: 零件序列，零件用名称作为标识，已知长度，格式为[编号，长度]
    :return: 解格式
    """
    solve = []
    return solve
