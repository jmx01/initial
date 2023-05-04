import copy
import random
import time
from decimal import Decimal

import matplotlib.pyplot as plt
import numpy as np

from initial_data import initial_data

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签


# 这个函数和standard_data_input函数可能相似
def merge(res_list):  # 合并所有长度相同的余料的函数
    output = copy.deepcopy(res_list)
    ans = []
    for i in range(len(output)):
        if not output[i]:
            continue
        for j in range(i + 1, len(output)):
            if output[i] and output[j] and output[i][1] == output[j][1] and output[i][3] == output[j][3]:
                output[i][2] += output[j][2]
                output[j] = []
    for o in output:
        if o:
            ans.append(o)
    return ans


def cal_fitness(solution_in, product0, matrix0):
    """
    计算适应度
    :param solution_in:某个子个体
    :param product0:产品管读取时的样子
    :param matrix0:禁接矩阵
    :return:（适应度，切割方法）
    """
    fitness = 0
    solution = copy.deepcopy(solution_in)
    product0 = copy.deepcopy(product0)  # 不能删这个，因为我们用的一直是最初的product0，不能改变
    unused_list = []
    flag = True

    for s_in in solution:
        raw_length = s_in[1]  # 被研究原料管s的长度
        raw_num = s_in[2]  # 被研究的原料管s剩余的数量，开始赋值为s的总数
        used_num = s_in[0][0]  # 用于统计该组原料管被用了多少根
        original_start_num = used_num
        total_num_of_s = raw_num  # 用于保存原料管s的总数
        for p in product0:  # 这个循环用于将选中的s，即原料管，填入产品管中
            if p[8]:  # 若该产品管已完成，则直接研究下一根产品管
                continue
            if (p[5] - data.pick_up < p[3] <= p[5] and p[3] + raw_length < p[6] and p[4] != p[6]) or (
                    p[4] == p[6] and p[3] == p[5] and p[3] + raw_length < p[6]):
                # 若目前的原料管受到禁接区约束限制，无法添加到当前研究的产品管是，则直接研究下一根产品管
                continue
            if raw_num >= p[1]:  # 若原料管数量大于当前研究的产品管组，则可在原料管不变的条件下继续到下一根产品管
                raw_num -= p[1]
                temp = p[1]
                s_in[0][0] = used_num  # 原料管分批
                used_num += p[1]
                s_in[0][1] = used_num - 1  # 原料管分批
                s_in[2] = s_in[0][1] - s_in[0][0]  # 改变对当前组原料管的总数的统计
            elif raw_num == 0:  # 若原料管用完且不缺，则尝试放入下一组原料管
                s_in[0][0] = used_num  # 原料管分批
                s_in[0][1] = original_start_num + total_num_of_s  # 原料管分批
                s_in[2] = s_in[0][1] - s_in[0][0] + 1  # 改变对当前组原料管的总数的统计
                break
            else:  # 若原料管不足，则需要将当前研究的产品管分为两组，一组全是装上原料管的，另一组全是没有的
                s_in[0][0] = used_num  # 原料管分批
                s_in[0][1] = original_start_num + total_num_of_s - 1  # 原料管分批
                s_in[2] = s_in[0][1] - s_in[0][0] + 1  # 改变对当前组原料管的总数的统计
                temp, copy_p = raw_num, copy.deepcopy(p)
                copy_p[1] = p[1] - raw_num
                product0.insert(product0.index(p) + 1, copy_p)
                p[1], raw_num = temp, 0
            process(s_in, p, matrix0[p[-1]], raw_length, temp)  # 具体的原料管安装到产品管的步骤
        if raw_num > 0:  # 若原料管有尚未使用完的，则放入unused list之中备用
            s_in[2] = raw_num
            s_in[0][0] = used_num  # 原料管分批
            s_in[0][1] = original_start_num + total_num_of_s  # 原料管分批
            unused_list.append(s_in)
        if solution.index(s_in) == len(solution) - 1:  # 若已遍历到原料管组列表中的最后一个原料管组，则将每个product[9]中存放的所有余料放入res_list中
            res_list = []
            for p in product0:
                if not p[8]:  # 若有未完成的产品管，则改变flag，使循环能够继续，否则保持flag为True，让外部大循环结束
                    flag = False
                for r in p[9]:
                    res_list.append(r)
                p[9] = []
            # res_list = merge(res_list)     # 最好先不使用merge函数
            add_list = unused_list + res_list
            add_list.sort(key=lambda func: int(func[1] * func[2]),
                          reverse=True)  # 将unused和res列表中所有元素放到一起并降序排列，重新放入解列表中继续运转
            solution += add_list
            if flag:
                break

    for p in product0:
        fitness += p[1] * p[7]
        if not p[3] == p[4]:
            fitness = -1
            break
    return fitness, product0


def process(s, p, matrix0, raw_length, raw_num):
    s[2] = raw_num
    temp_length = p[3] + raw_length
    used_length = 0
    flag = False

    if temp_length <= p[5]:  # 若安装整段原料管不会进入下个禁接区，则直接将其装上去
        p[3] = temp_length
        p[2].append(copy.deepcopy(s))
        p[7] += 1
    elif temp_length >= p[6]:  # 若安装整段整段原料管会超过下个禁接区，则分情况讨论
        if temp_length >= p[4]:  # 超过全长
            used_length = p[4] - p[3]
            temp = [copy.deepcopy(s[0]), used_length, raw_num, s[-1]]
            temp2 = [temp[0], s[1] - temp[1], raw_num, s[-1]]
            p[3] = p[4]
            p[2].append(temp)
            p[7] += 1
            p[8] = True

            if temp2[1] >= data.pick_up:  # 余料小于指定长度（data.pick_up）的不要
                p[9].append(temp2)
        else:  # 未超过全长
            p[3] = temp_length
            p[7] += 1
            for m in matrix0:
                if m[0] < temp_length < m[1]:  # 落在禁接区之内
                    p[5], p[6] = m[0], m[1]
                    used_length = p[5] - p[3] + raw_length
                    flag = True
                    break
                elif m[0] >= temp_length:  # 在禁接区之前
                    p[5], p[6] = m[0], m[1]
                    p[2].append(copy.deepcopy(s))
                    break
                elif matrix0.index(m) == len(matrix0) - 1:  # 已超过最后一个禁接区
                    p[5], p[6] = p[4], p[4]
                    p[2].append(copy.deepcopy(s))
                    break

    else:  # 若下一段管正好落在下一个禁接区之中
        if p[5] == p[3]:  # 若下一段管全部落在禁接区之内时。（这个语句似乎没用）
            return p
        p[7] += 1
        used_length = p[5] - p[3]
        flag = True
    if flag:
        temp = [copy.deepcopy(s[0]), used_length, raw_num, s[-1]]
        temp2 = [temp[0], s[1] - temp[1], raw_num, s[-1]]
        p[3] = p[5]
        p[2].append(copy.deepcopy(temp))
        if temp2[1] >= data.pick_up:  # 余料小于指定长度（data.pick_up）的不要
            p[9].append(temp2)


def read_excel(data0):
    """
    读数据，生成第一个子个体，禁接区，产品管矩阵
    :param data0: initial_data()类数据
    :return: 禁接区，产品管矩阵，子个体
    """
    read_output = data0.datatable_output
    matrix0 = []  # 将多个禁接列表装在matrix列表中，构成禁接矩阵。
    product0 = []  # 对原料管的读取和一些准备工作
    cpy_output = []
    for i in range(len(read_output)):
        cpy_output.append(read_output.loc[i].tolist())

    if data0.connection:  # 进行原料管虚焊操作
        index = list(range(len(data0.datatable_output)))
        random.shuffle(index)
        for i in range(len(index)):
            cpy_output[index[i]] = [*cpy_output[index[i]], index[i]]
        for j in range(len(cpy_output) - 1):
            k = j
            add_matrix = data0.change_zone(index)[0]
            removed_i = cpy_output[j][-1]
            index.remove(removed_i)
            if j == 0:
                product_num = cpy_output[j][1]
            else:
                product_num = cpy_output[j + 1][1] - cpy_output[j][1]
            if product_num == 0:
                k -= 1
                continue
            total_len = 0
            for tmp in cpy_output:
                total_len += Decimal(str(tmp[2])).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
            product0 += [
                [cpy_output, product_num, [], 0, total_len, add_matrix[0][0], add_matrix[0][1], 0, False,
                 [], k]]
            matrix0.append(add_matrix)

    else:  # 不进行原料管虚焊操作
        for i in range(len(data0.datatable_output)):
            matrix0 += [data0.change_zone([i])[0]]
            total_len = Decimal(str(cpy_output[i][2])).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
            product_num = int(cpy_output[i][1])
            product0 += [
                [[cpy_output[i]], product_num, [], 0, total_len, matrix0[i][0][0], matrix0[i][0][1], 0, False, [], i]]

    "原料管处理"
    read_input = data0.dt_input
    raw = []
    for i in range(len(read_input)):
        raw.append(read_input.loc[i].tolist())
        part_sum, n, length = 1, int(raw[-1][1]), raw[-1][2]
        del raw[-1]
        raw.append([[part_sum, n], length, n, length])
    return matrix0, product0, raw


def initialize(data0):
    """
    初始化，生成种群，产品管，禁接区
    :param data0:initial_data()类的数据
    :return:初始种群
    """
    "读取数据"
    matrix0, product0, this = read_excel(data)
    "生成种群，添加适应度,并按适应度排序"
    groups = []
    for i in range(data0.algorithm_solution_quantity):
        random.shuffle(this)
        groups.append(copy.deepcopy(this))
        fitness = cal_fitness(groups[-1], product0, matrix0)
        while fitness == -1 or fitness[0] < data0.total_num:
            random.shuffle(groups[-1])
            fitness = cal_fitness(groups[-1], product0, matrix0)
        groups[-1].append(fitness)
    groups.sort(key=lambda func: func[-1][0])
    return groups, product0, matrix0


def ox(solution1, solution2):
    """
    交换函数，交换两个等长列表的部分指定区域
    :param solution1: 列表1
    :param solution2: 列表2
    :return: [子列表1，子列表2]
    """
    "找两个不一样的点"
    rand = random.sample(range(0, len(solution1) - 1), 2)
    min_rand, max_rand = min(rand), max(rand)
    "生成不变区域"
    copy_mid = [solution1[min_rand:max_rand + 1], solution2[min_rand:max_rand + 1]]
    "生成改变区域"
    s1_head = solution1[:min_rand]
    s1_head.reverse()
    s1_tail = solution1[max_rand + 1:]
    s1_tail.reverse()
    s2_head = solution2[:min_rand]
    s2_head.reverse()
    s2_tail = solution2[max_rand + 1:]
    s2_tail.reverse()
    swap = [s2_head + s2_tail, s1_head + s1_tail]
    "生成子列表"
    c_new = []
    for ix in range(2):
        c_swap = []
        while swap[ix]:
            tmp = swap[ix].pop()
            if tmp not in copy_mid[ix]:
                c_swap.append(tmp)
        for c in copy_mid[1 - ix]:
            if c not in copy_mid[ix]:
                c_swap.append(c)
        c_new.append(c_swap[len(solution1) - max_rand - 1:] + copy_mid[ix] + c_swap[:len(solution1) - max_rand - 1])

    return c_new


def cross(groups, product0, matrix0):
    """
    遗传函数，用来生成新的种群
    :param groups:上一代种群
    :param product0:产品管矩阵
    :param matrix0:产品管禁接区
    :return:新种群
    """
    "找到父母个体"
    rand = [random.sample(range(0, len(groups) - 1), 2), random.sample(range(0, len(groups) - 1), 2)]
    index1 = np.where(groups[rand[0][0]][-1][0] < groups[rand[0][1]][-1][0], rand[0][0], rand[0][1])
    index2 = np.where(groups[rand[1][0]][-1][0] < groups[rand[1][1]][-1][0], rand[1][0], rand[1][1])
    parent1 = copy.deepcopy(groups[index1][:-1])
    parent2 = copy.deepcopy(groups[index2][:-1])
    "生成一个子个体"
    children = ox(parent1, parent2)
    index = np.where(random.random() > 0.5, 0, 1)
    children = children[index]
    "替换适应度靠后的种群个体"
    rand_replace = random.randint(len(groups) // 2, len(groups) - 1)
    groups[rand_replace] = children
    f_c = cal_fitness(children, product0, matrix0)
    if f_c[0] < data.total_num or f_c == -1:
        random.shuffle(children)
        f_c = cal_fitness(children, product0, matrix0)
    groups[rand_replace].append(f_c)
    groups.sort(key=lambda func: func[-1][0])  # 按适应度排序


def separate_connection(finished_product):
    separate_product = []
    return separate_product


def display_raw(finished_product):  # 用于记录原料管切割情况
    all_raw_part = []
    for fp in finished_product:
        raws = fp[2]
        for r in raws:
            all_raw_part.append(r)
    all_raw_part.sort(key=lambda func: func[3])
    return all_raw_part


def fit_list_plot(fit):
    plt.plot(fit)
    plt.title("焊点数迭代过程")
    plt.xlabel("迭代次数")
    plt.ylabel("焊点数")
    plt.show()


if __name__ == '__main__':
    start = time.time()
    data = initial_data()
    total_num = data.total_num  # 产品管总数
    group_initial, product, matrix = initialize(data)
    fit_opt, pro_opt = group_initial[0][-1][0], group_initial[0][-1][1]
    fit_list = [fit_opt - total_num]

    for x in range(data.num):
        cross(group_initial, product, matrix)
        fit_list.append(group_initial[0][-1][0] - total_num)
    fit_opt, pro_opt = group_initial[0][-1][0], group_initial[0][-1][1]

    # fit_list_plot(fit_list)  # 对迭代的绘图
    raw_cut_method = display_raw(pro_opt)
    if data.show_composition:
        [print(p[0:3] + p[-4:]) for p in pro_opt]
    print("焊点数为%d" % (fit_opt - total_num))
    print("此次消耗时间为%f" % (time.time() - start))
