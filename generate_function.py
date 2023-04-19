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
            length[address] = 100000000
            address = length.argmin()

    fetch = table[address, :].copy()  # fetch为复制的table第i+1行的信息
    fetch[1] = 1  # 拿走的数量为1
    table[address, 1] -= 1  # 数量-1
    return table, fetch


# 暂时废用此函数
def change_solution(GS_new, string):
    """
    将解进行转化，便于另外两人进一步处理(大概率用不上了)
    :param GS_new: 蒋孟欣格式的解
    :param string: 判断将解转化为何种形式，meng为转化为孟歆尧的解，yuan为转化为袁浩的解
    :return:一个转化好的解
    """
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
                change_zone[1].append(no_pick_zone[index, 1][0][x][cc])  # 将禁接区加到change_zone上

    change_zone, change_zone_cal = standard_no_pick_zone([change_zone])  # 生成变化后禁接区和累积禁接区
    change_zone_cal = change_zone_cal[0][1]

    return 0
    # i = 0  # 第几根原料管
    # j = 0  # 在第几个禁接区
    # k = [0, 0]  # 覆盖零件管区间
    # while cal_ma[1] < cut_num[-1] and i <= len(solve)-1:  # 当前原料总长小于零件管总长，且仍有原料管时
    #     cal_ma[1] = cal_ma[0] + solve[i]
    #     solve.insert(i, [solve[i], 0, [], 0, 0])
    #     del solve[i + 1]
    #
    #     while cal_ma[1] > change_zone_cal[j][0]:
    #         j += 1
    #
    #
    #     if j != 0:
    #         over = cal_ma[1] - change_zone_cal[j - 1][0]  # 超出上一个区域长度
    #     else:
    #         over = cal_ma[1]
    #
    #     if change_zone_cal[j][1] == 0:  # 判断剩余长度
    #         if over >= solve[i][0]:
    #             solve[i][1], solve[i][3] = solve[i][0], solve[i][0]
    #             solve[i].append(1)
    #         else:
    #             solve[i].append(2)
    #     else:
    #
    #     cal_ma[0] = cal_ma[1]
    #     k[0] = k[1]
    #     i += 1
    #
    # if cal_ma[] > cut_num[-1] and i <= len(solve):
    #     return solve
    # else:
    #     print("序列解生成出错")
    #     return 0


data = initial_data()
