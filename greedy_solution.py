import copy
import time
from decimal import Decimal

import numpy as np
import pandas as pd

from generate_function import is_continue, MM_fetchOne
from initial_data import initial_data


def list_to_team(ma_input):
    ma = copy.deepcopy(ma_input)
    for i in range(len(ma)):
        epoch = []
        epoch.extend(copy.deepcopy(ma[i][2]))
        epoch.append(copy.deepcopy(ma[i][3]))
        epoch.append(copy.deepcopy(ma[i][4]))
        length = ma[i][0]  # 此类原料管长度
        num = 1  # 此类原料管数量
        odd = 1 - ma[i][-1] / length
        last = ma[i][-1]
        use = length - last
        ma[i] = []
        for j in range(len(epoch)):
            if epoch[j] != 0:
                ma[i].append(epoch[j])
        if len(ma[i]) != 0:
            ma[i].sort()
        ma[i] = [length, num, use, last, odd, ma[i]]
    return ma


def in_team(ma):
    """将原料管输出转化为组批输出"""
    ma_new = []
    split_method = []
    for i in range(len(ma)):
        if ma[i][-1] not in split_method:
            split_method.append(copy.deepcopy(ma[i][-1]))
            ma_new.append(copy.deepcopy(ma[i]))
        else:
            ma_new[split_method.index(ma[i][-1])][1] += 1

    pd.DataFrame(copy.deepcopy(ma_new),
                 columns=["此组原料管长度", "此组原料管数量", "此组管每根使用长度", "此组管每根舍弃长度",
                          "此组原料管利用率", "此组原料管切割方式"]).to_excel("./原料管组批切割序列.xlsx")
    return ma_new, split_method


def weld_point_num(ma_input):
    count = 0
    for i in range(len(ma_input)):
        if ma_input[i][3] == 0:
            count += 1
    count = len(ma_input) - 1 - count
    return count


class greedy_solve(object):
    data = initial_data()

    greedy_solution_quantity = data.greedy_solution_quantity  # 需要的贪婪解初始数
    over_time = data.over_time  # 初始解生成时间限制
    pick_up = data.pick_up  # 可放弃的新生成的原材料长度
    alpha = data.alpha  # 建议离禁焊区的距离
    e = data.e  # 概率随机取值

    material_length = data.material_length  # 输入材料总长度
    product_length = data.product_length  # 输出材料总长度

    datatable_output = data.datatable_output
    deal_no_pick_zone = data.deal_no_pick_zone
    dt_input = data.dt_input
    no_pick_zone, calculate_no_pick_zone = data.no_pick_zone, data.calculate_no_pick_zone

    def __generate_tube_zone(self, x):
        npz = np.array(self.no_pick_zone)

        name = npz[:, 0]
        name = int(np.where(name == x)[0])
        np_out = self.calculate_no_pick_zone[name][1]
        np_out = np.array(np_out)
        return np_out

    def __deal_in_out(self, fetch_in_res, fetch_out, k, dt_in):
        res = 0
        use_res = k  # 被使用的剩余长度
        done = 1  # 没有切割
        np_out = self.__generate_tube_zone(fetch_out[0])

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

        if res > self.pick_up:  # 将新的解加入dt_in中
            dt_in = pd.DataFrame(dt_in)
            # add element
            dt_in.loc[dt_in.shape[0]] = [dt_in.shape[0] + 1, 1, res]

            dt_in = np.array(dt_in)

        return dt_in, use_res, fetch_out, done

    def solve_1(self):
        dt_in = copy.deepcopy(self.dt_input)
        dt_out = copy.deepcopy(self.datatable_output)
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
            if time_break > self.over_time:
                return 10  # 错误警告，单个初始解超时判别

            while fetch_in_res >= fetch_out[2]:  # 当剩余长度大于等于取出长度
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

                dt_in, useful_part, fetch_out, done = self.__deal_in_out(fetch_in_res, fetch_out, ma_input[-1][1],
                                                                         dt_in)
                ma_input[-1][3] = useful_part

                if is_continue(dt_in) and (sum(dt_in[:, 1]) >= 1 or done):  # 在最后一个时会循环
                    dt_in, fetch_in = MM_fetchOne(dt_in)
                    fetch_in_res = fetch_in[2]
                    ma_input.append([fetch_in[2], fetch_in[2], cut_list, 0])
                else:
                    return 111  # 错误警告，原料管被用光

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
        ma = pd.DataFrame(ma,
                          columns=["原料长度", "剩余长度", "切割向量", "剩余长度中有效使用部分", "舍弃长度"])
        ma = ma.drop(ma[ma["原料长度"] == ma["舍弃长度"]].index)
        ma = np.array(ma).tolist()
        ma_input = copy.deepcopy(ma)  # 原来的input

        pd.DataFrame(copy.deepcopy(pro_output), columns=["产品管编号", "产品管长度"]).to_excel("./产品管生成序列.xlsx")

        ma_new = list_to_team(ma_input)
        team, split_method = in_team(ma_new)

        team_new = copy.deepcopy(team)
        for i in range(len(ma_new)):
            index_1 = split_method.index(ma_new[i][-1])
            index_2 = team[index_1][1] - team_new[index_1][1] + 1
            ma[i].append(index_1)
            ma[i].append(index_2)
            team_new[index_1][1] -= 1
        pd.DataFrame(copy.deepcopy(ma),
                     columns=["原料长度", "剩余长度", "切割向量", "剩余长度中有效使用长度", "舍弃长度",
                              "原料所属组批次", "该组批已使用根数"]).to_excel("./此次的原料切割通列.xlsx")

        weld = weld_point_num(ma)
        time3 = time.time()
        return [ma_input, pro_output], time3 - time1, team, weld
