import time
import numpy as np
import pandas as pd
import copy
import random

# 读数据  基本不变动
greedy_solution_quantity = 2  # 需要的贪婪解初始数
random_solution_quantity = 62  # 需要的随机解初始数
total_solution_quantity = greedy_solution_quantity + random_solution_quantity  # 总的解数
over_time = 3600  # 初始解生成时间限制
pick_up = 30  # 可放弃的新生成的原材料长度
alpha = 0  # 建议离禁焊区的距离
e = 0.05  # 概率随机取值
datatable_input = 'data_input.xlsx'  # 输入文件的路径
datatable_output = 'data_output.xlsx'  # 零件文件路径
# deal_no_pick_zone = 'zone.xlsx'  # 禁接区文件路径

datatable_input = pd.read_excel(datatable_input)  # [编号、数量、长度]  输入材料
datatable_output = pd.read_excel(datatable_output)  # [编号、数量、长度]  输出材料
# deal_no_pick_zone = pd.read_excel('deal_no_pick_zone')  # [编号、[区域长度、禁接标识（0或1）]]  未经处理的禁接区矩阵

# 示例禁接矩阵
deal_no_pick_zone = [
    ["7406104-B1-10010-5", [[1104, 1], [1300, 0], [900, 1], [1280, 0], [900, 1], [650, 0]]],
    ["7406104-B1-10011-2", [[1104, 1], [1300, 0], [900, 1], [1280, 0], [900, 1], [650, 0]]],
    ["7406104-B1-10012-2", [[1104, 1], [1300, 0], [900, 1], [1280, 0], [900, 1], [650, 0]]],
    ["7406104-B1-10013-2", [[1104, 1], [1300, 0], [900, 1], [1280, 0], [900, 1], [650, 0]]],
    ["7406104-B1-10014-2", [[1104, 1], [1300, 0], [900, 1], [1280, 0], [900, 1], [650, 0]]]
]

material_length = sum(np.array(datatable_input.iloc[:, 1]) * np.array(datatable_input.iloc[:, 2]))  # 输入材料总长度
product_length = sum(np.array(datatable_output.iloc[:, 1]) * np.array(datatable_output.iloc[:, 2]))  # 输出材料总长度


def should_begin(material, product):
    """
    :param material: 原材料总长度
    :param product: 输出材料总长度
    :return: bool，1为可以套管，0为不可套管
    """
    return material >= product


def standard_no_pick_zone(table):
    """
    //未完成
    :aid 处理禁接区（标准化禁接区）
    :param table: 输入的原始的禁接矩阵
    :return: 处理好后的标准禁接矩阵
    """
    # zone = np.array(table.copy(deep=True))
    zone = np.array(table)
    return zone


# 标准化原料
dt_input = datatable_input.copy(deep=True)  # 深复制镜像
dt_input = dt_input.groupby("长度").sum()  # 合并长度相同的行，index变为长度
dt_input["长度"] = dt_input.index
dt_input.index = range(len(dt_input["长度"]))  # 重新变为[编号，数量，长度]的形式

# 标准化禁接区,[编号、[累积区域长度、禁接标识（0或1）]]
no_pick_zone = standard_no_pick_zone(deal_no_pick_zone)


def e_rule(string):
    """
    :param string: 一个字符
    :return: 按规则返回原字符或相反的字符
    """
    number = random.random()
    if string == "max":
        if number < e:
            return "min"
        else:
            return string
    else:
        if number < e:
            return "max"
        else:
            return string


def MM_fetchOne(table, MaxOrMin="max"):
    """
    默认table不为空
    最大或最小的一根  # 默认取最大的一根
    :param MaxOrMin: 标识符
    :param table: 原料或零件的镜像
    :return: 新的table和那根材料的名称数量和长度
    """
    fetch = [0, 0, 0]  # 初始化取的材料
    address = 0  # 初始化取的材料的位置
    table = np.array(table)
    quantity = table[:, 1].copy()
    length = table[:, 2].copy()
    MaxOrMin = e_rule(MaxOrMin)

    if MaxOrMin == "max":  # 取最大的一根
        for i in range(len(quantity)):
            if quantity[i] > 0 and length[i] > fetch[2]:
                address = i
                fetch[2] = length[i]
    else:  # 取最小的一根
        fetch[2] = 1000000  # 一个很大的常数,用来方便后续处理
        for i in range(len(quantity)):
            if quantity[i] > 0 and length[i] < fetch[2]:
                address = i
                fetch[2] = length[i]

    fetch = table[address, :].copy()  # fetch为复制的table第i+1行的信息
    fetch[1] = 1  # 拿走的数量为1
    table[address, 1] -= 1  # 数量-1
    return table, fetch


def is_continue(dt):
    """
    判断零件管是否用完
    :param dt: 零件管的镜像，一直在改变的值
    :return: 0或1
    """
    dt = pd.DataFrame(dt)
    for i in dt.loc[:, 1]:
        if i > 0:
            return 1  # 未用完
    else:
        return 0  # 已用完


def deal_in_out(fetch_in_res, fetch_out, k, dt_in, npz=no_pick_zone):
    """
    :param dt_in: 当前所有的原料管
    :param fetch_in_res:当前剩下的原料管的长度
    :param fetch_out:正在取出的零件管的长度
    :param k:剩余长度
    :param npz:零件管的禁接区
    :return:新的原料管，切下的长度，现在缺少的管材长度
    """
    res = 0
    use_res = k  # 被使用的剩余长度
    done = 1  # 没有切割
    npz = np.array(npz)

    name = npz[:, 0]
    name = np.where(name == fetch_out[0])

    np_out = npz[name][0][1]
    np_out = np.array(np_out)

    # 把np_out变为累加形式，这一些可以统一放在前面当作一个函数，拿处理好的东西传参
    for i in range(len(np_out[:, 0]) - 1):
        np_out[i + 1, 0] += np_out[i, 0]  # [区域尾累加，该区域标识]

    for i in range(len(np_out)):
        if np_out[i, 0] > fetch_in_res:
            if np_out[i, 1] == 0:  # 在非禁接区
                break
            else:  # 在禁接区
                if i > 0:
                    res = fetch_in_res - np_out[i - 1, 0]
                else:
                    res = fetch_in_res
                use_res = use_res - res
                done = 0
                break

    fetch_out[2] = fetch_out[2] + res - fetch_in_res

    if res > pick_up:  # 将新的解加入dt_in中
        dt_in = pd.DataFrame(dt_in)
        # add element
        dt_in.loc[dt_in.shape[0]] = [dt_in.shape[0] + 1, 1, res]

        dt_in = np.array(dt_in)

    return dt_in, use_res, fetch_out, done


def greedy_Solution(dt_in=dt_input, dt_out=datatable_output):
    """
    贪婪解
    :param dt_in: 处理好的原料的镜像
    :param dt_out: 零件管的镜像
    :return:一个贪婪解，可以引入ε原则随机取
    """
    ma_input = []  # [[原料长度，剩余长度,[切割长度]，剩余长度的使用长度]]
    pro_output = []  # [[零件管编号，长度]]
    time1 = time.time()  # 开启一次贪婪解的初始时间
    fetch_in_res = 0  # 原料剩下的长度
    cut_list = []  # 每根原料的切割列表

    dt_out, fetch_out = MM_fetchOne(dt_out, "min")  # 先取一个零件管，更新数量
    pro_output.append([fetch_out[0], fetch_out[2]])  # 添加到取出的零件管集中
    dt_in, fetch_in = MM_fetchOne(dt_in)  # 再取一个原料管
    ma_input.append([fetch_in[2], fetch_in[2], cut_list, 0])  # 添加到原料管集中
    fetch_in_res += fetch_in[2]

    while is_continue(dt_out) or fetch_out[2] != 0:  # 当原料管还有剩余，或者拿出的零件管长度不为0
        time2 = time.time()
        time_break = time2 - time1
        if time_break > over_time:
            return 0  # 单个初始解超时判别

        while fetch_in_res >= fetch_out[2]:  # 当剩余长度大于取出长度
            if len(cut_list) == 0:
                cut_list.append(fetch_out[2] - ma_input[-1][3])  # 如果是初次切割，减去上根原料剩余长度使用部分。
            else:
                cut_list.append(fetch_out[2])
            fetch_in_res -= fetch_out[2]
            ma_input[-1][1] -= fetch_out[2]
            fetch_out[2] = 0
            if is_continue(dt_out):  # 判断零件管是否用完
                dt_out, fetch_out = MM_fetchOne(dt_out, "min")
                pro_output.append([fetch_out[0], fetch_out[2]])
            else:
                break

        while fetch_in_res < fetch_out[2]:
            ma_input[-1][2] = copy.deepcopy(cut_list)  # 把切割长度存下
            cut_list = []

            dt_in, useful_part, fetch_out, done = deal_in_out(fetch_in_res, fetch_out, ma_input[-1][1], dt_in)
            ma_input[-1][3] = useful_part

            if is_continue(dt_in) and (sum(dt_in[:, 1]) >= 1 or done):  # 在最后一个时会循环
                dt_in, fetch_in = MM_fetchOne(dt_in)
                fetch_in_res = fetch_in[2]
                ma_input.append([fetch_in[2], fetch_in[2], cut_list, 0])
            else:
                return 1  # 原料管被用光

    for ele in ma_input:
        ele.append(ele[1] - ele[3])

    # 对原料管的处理
    dt_in = pd.DataFrame(dt_in)
    dt_in.columns = ["编号", "数量", "长度"]
    dt_in = dt_in.groupby("长度").sum()
    dt_in = dt_in[dt_in["数量"] > 0]
    dt_in["长度"] = dt_in.index.tolist()
    dt_in.index = range(dt_in.shape[0])
    dt_in.to_excel("./此次切割剩余原料.xlsx")

    # 下两行用来检测ma_input
    ma = copy.deepcopy(ma_input)
    ma = pd.DataFrame(ma, columns=["原料长度", "剩余长度", "切割向量", "剩余长度中有效使用部分", "每根原料管剩余长度"])
    ma.to_excel("./某一次的原料切割方式.xlsx")
    ma = ma.drop(ma[ma["原料长度"] == ma["每根原料管剩余长度"]].index)
    ma.to_excel("./某一次的原料切割方式——new.xlsx")
    cc = np.array(ma)
    ma_input = cc.tolist()

    return [ma_input, pro_output]


def meng_list(GS_new):
    GM = copy.deepcopy(GS_new)
    meng_1 = [[0], []]
    meng_2 = [0]
    meng_3 = []
    ma_in = pd.DataFrame(GM[0])

    del ma_in[4]
    del ma_in[3]
    del ma_in[1]

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
        if i[4] > 0:
            i.append(1)
        else:
            i.append(0)

        i.append(len(i[2]))

    for i in range(ma_in.shape[0] - 1):
        ma[i + 1][6] = ma[i + 1][6] + ma[i][6]
        if ma[i+1][5] == 1:
            meng_2.append(ma[i+1][6]+1)

    GS = [meng_1, meng_2, meng_3]
    return GS


def yuan_list(GS_new):
    GY = copy.deepcopy(GS_new)
    return GY


def random_Solution(dt_in=dt_input, dt_out=datatable_output, npz=no_pick_zone):
    """
    //统一孟歆尧的部份
    :param dt_in:
    :param dt_out:
    :param npz:
    :return:
    """
    return 0


def main():
    initial = []  # 生成64个初始解，2个贪婪解，62个随机解
    meng_solution = []  # 孟歆尧的解
    yuan_solution = []  # 袁浩要的解的形式

    if should_begin(material_length, product_length):

        # 贪婪解
        count = 0
        while count < greedy_solution_quantity:
            GS_new = greedy_Solution()  # 新生成的贪婪解
            if GS_new != 0 and GS_new != 1 and GS_new not in initial:
                initial.append(GS_new)
                meng_solution.append(meng_list(GS_new))
                yuan_solution.append(yuan_list(GS_new))
                count += 1
            else:
                print("GS_new生成出错，生成新的初始解")

        # 随机解
        # count = 0
        # while count < random_solution_quantity:
        #     RS_new = random_Solution()  # 新生成的初始解
        #     if RS_new != 0 and RS_new not in initial:
        #         initial.append(RS_new)
        #         meng_solution.append(meng_list(RS_new))
        #         yuan_solution.append(yuan_list(RS_new))
        #         count += 1
        #     else:
        #         print("RS_new生成出错，生成新的初始解")

        return initial, meng_solution, yuan_solution  # 返回初始解的集

    else:
        return "原料过短，无法套管"


main()
