import copy
import random
import time
from decimal import Decimal

import numpy as np

from initial_data import initial_data


def ox(solution1, solution2):
    # 生成两个不一样的值
    rand = random.sample(range(0, len(solution1) - 1), 2)
    min_rand, max_rand = min(rand), max(rand)

    copy_mid = [solution1[min_rand:max_rand + 1], solution2[min_rand:max_rand + 1]]
    s1_head = solution1[:min_rand]
    s1_head.reverse()
    s1_tail = solution1[max_rand + 1:]
    s1_tail.reverse()
    s2_head = solution2[:min_rand]
    s2_head.reverse()
    s2_tail = solution2[max_rand + 1:]
    s2_tail.reverse()
    swap = [s2_head + s2_tail, s1_head + s1_tail]

    c_new = []
    for x in range(2):
        c_swap = []
        while swap[x]:
            tmp = swap[x].pop()
            if tmp not in copy_mid[x]:
                c_swap.append(tmp)
        for c in copy_mid[1 - x]:
            if c not in copy_mid[x]:
                c_swap.append(c)
        c_new.append(c_swap[len(solution1) - max_rand - 1:] + copy_mid[x] + c_swap[:len(solution1) - max_rand - 1])

    return c_new


## 这个函数和standard_data_input函数可能相似
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


def cal_fitness(solution_in, product, matrix):
    fitness = 0
    solution = copy.deepcopy(solution_in)
    unused_list = []
    flag = True

    for s in solution:
        raw_length = s[1]  # 被研究原料管s的长度
        raw_num = s[2]  # 被研究的原料管s剩余的数量，开始赋值为s的总数
        used_num = s[0][0]  # 用于统计该组原料管被用了多少根
        original_start_num = used_num
        total_num_of_s = raw_num  # 用于保存原料管s的总数
        for p in product:  # 这个循环用于将选中的s，即原料管，填入产品管中
            s_in = copy.deepcopy(s)
            if p[8]:  # 若该产品管已完成，则直接研究下一根产品管
                continue
            if p[5] - data.pick_up < p[3] <= p[5] and p[3] + raw_length < p[6] and p[4] != p[6] or p[4] == p[6] and p[
                3] == p[5] \
                    and p[3] + raw_length < p[6]:
                # 若目前的原料管受到禁接区约束限制，无法添加到当前研究的产品管是，则直接研究下一根产品管
                continue
            if raw_num >= p[1]:  # 若原料管数量大于当前研究的产品管组，则可在原料管不变的条件下继续到下一根产品管
                raw_num -= p[1]
                temp = p[1]
                s_in[0][0] = used_num  # 原料管分批
                used_num += p[1]
                s_in[0][1] = used_num  # 原料管分批
                s_in[2] = s_in[0][1] - s_in[0][0]  # 改变对当前组原料管的总数的统计
            elif raw_num == 0:  # 若原料管用完且不缺，则尝试放入下一组原料管
                s_in[0][0] = used_num  # 原料管分批
                s_in[0][1] = original_start_num + total_num_of_s  # 原料管分批
                s_in[2] = s_in[0][1] - s_in[0][0]  # 改变对当前组原料管的总数的统计
                break
            else:  # 若原料管不足，则需要将当前研究的产品管分为两组，一组全是装上原料管的，另一组全是没有的
                s_in[0][0] = used_num  # 原料管分批
                s_in[0][1] = original_start_num + total_num_of_s  # 原料管分批
                s_in[2] = s_in[0][1] - s_in[0][0]  # 改变对当前组原料管的总数的统计
                temp = raw_num
                loc = product.index(p)
                copy_p = copy.deepcopy(p)
                copy_p[1] = p[1] - raw_num
                product.insert(loc + 1, copy_p)
                p[1] = temp
                raw_num = 0
            process(s_in, p, matrix[p[-1]], raw_length, temp)  # 具体的原料管安装到产品管的步骤
        if raw_num > 0:  # 若原料管有尚未使用完的，则放入unused list之中备用
            s_copy = copy.deepcopy(s)
            s_copy[2] = raw_num
            s_copy[0][0] = used_num  # 原料管分批
            s_copy[0][1] = original_start_num + total_num_of_s  # 原料管分批
            unused_list.append(s_copy)
        if solution.index(s) == len(solution) - 1:  # 若已遍历到原料管组列表中的最后一个原料管组，则将每个product[9]中存放的所有余料放入res_list中
            res_list = []
            for p in product:
                if not p[8]:  # 若有未完成的产品管，则改变flag，使循环能够继续，否则保持flag为True，让外部大循环结束
                    flag = False
                res = copy.deepcopy(p[9])
                p[9] = []
                for r in res:
                    res_list.append(r)
            # res_list = merge(res_list)     # 最好先不使用merge函数
            add_list = unused_list + res_list
            add_list.sort(key=lambda add_list: int(add_list[1] * add_list[2]),
                          reverse=True)  # 将unused和res列表中所有元素放到一起并降序排列，重新放入解列表中继续运转
            solution += add_list
            if flag:
                break

    for p in product:
        fitness += p[1] * p[7]
        if not p[3] == p[4]:
            fitness = -1
            break
    return fitness, product


def process(s_in, p, matrix, raw_length, raw_num):
    s = copy.deepcopy(s_in)
    s[2] = raw_num
    temp_length = p[3] + raw_length
    if temp_length <= p[5]:  # 若安装整段原料管不会进入下个禁接区，则直接将其装上去
        p[3] = temp_length
        p[2].append(s)
        p[7] += 1
    elif temp_length >= p[6]:  # 若安装整段整段原料管会超过下个禁接区，则分情况讨论
        if temp_length >= p[4]:  # 超过全长
            used_length = p[4] - p[3]
            p[3] = p[4]
            temp = copy.deepcopy(s)
            temp[2] = raw_num
            temp[1] = used_length
            p[2].append(temp)
            p[7] += 1
            p[8] = True
            temp2 = copy.deepcopy(temp)
            temp2[1] = s[1] - used_length
            temp2[2] = raw_num
            if temp2[1] >= data.pick_up:  # 余料小于指定长度（data.pick_up）的不要
                p[9].append(temp2)
        else:  # 未超过全长
            p[3] = temp_length
            p[7] += 1
            for m in matrix:
                if m[0] < temp_length < m[1]:  # 落在禁接区之内
                    p[5], p[6] = m[0], m[1]
                    used_length = p[5] - p[3] + raw_length
                    p[3] = p[5]
                    temp = copy.deepcopy(s)
                    temp[2] = raw_num
                    temp[1] = used_length
                    p[2].append(temp)
                    temp2 = copy.deepcopy(temp)
                    temp2[1] = s[1] - used_length
                    temp2[2] = raw_num
                    if temp2[1] >= data.pick_up:  # 余料小于指定长度（data.pick_up）的不要
                        p[9].append(temp2)
                    break
                if m[0] >= temp_length:  # 在禁接区之前
                    p[5], p[6] = m[0], m[1]
                    p[2].append(s)
                    break
                if matrix.index(m) == len(matrix) - 1:  # 已超过最后一个禁接区
                    p[5], p[6] = p[4], p[4]
                    p[2].append(s)
                    break

    else:  # 若下一段管正好落在下一个禁接区之中
        if p[5] == p[3]:  # 若下一段管全部落在禁接区之内时。（这个语句似乎没用）
            return p
        p[7] += 1
        used_length = p[5] - p[3]
        p[3] = p[5]
        temp = copy.deepcopy(s)
        temp[2] = raw_num
        temp[1] = used_length
        p[2].append(temp)
        temp2 = copy.deepcopy(temp)
        temp2[1] = s[1] - used_length
        if temp2[1] >= data.pick_up:  # 余料小于指定长度（data.pick_up）的不要
            p[9].append(temp2)


def read_excel(data0):
    index = list(range(len(data0.datatable_output)))
    random.shuffle(index)

    matrix = []  # 将多个禁接列表装在matrix列表中，构成禁接矩阵。
    product = []  # 对原料管的读取和一些准备工作
    read_output = data0.datatable_output
    tmp_output = []
    for i in range(len(read_output)):
        tmp_output.append(read_output.loc[i].tolist())
    cpy_output = copy.deepcopy(tmp_output)

    if data0.connection:  # 进行原料管虚焊操作
        for i in range(len(index)):
            tmp_output[i] = cpy_output[index[i]][:]
            tmp_output[i].append(index[i])
        cpy_output = copy.deepcopy(tmp_output)
        cpy_output.sort(key=lambda cpy_output: cpy_output[1])
        for j in range(len(tmp_output) - 1):
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
            for tmp in tmp_output:
                total_len += Decimal(str(tmp[2])).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
            product += [
                [copy.deepcopy(tmp_output), product_num, [], 0, total_len, add_matrix[0][0], add_matrix[0][1], 0, False,
                 [], k]]
            matrix.append(add_matrix)
            tmp_output.remove(cpy_output[j - 1])
        total_num = sum([p[1] for p in product])

    else:  # 不进行原料管虚焊操作
        for i in range(len(data0.datatable_output)):
            matrix += [data0.change_zone([i])[0]]
        for i in range(len(read_output)):
            total_len = Decimal(str(cpy_output[i][2])).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
            product_num = int(tmp_output[i][1])
            product += [
                [[cpy_output[i]], product_num, [], 0, total_len, matrix[i][0][0], matrix[i][0][1], 0, False, [], i]]
        total_num = sum([p[0][0][1] for p in product])

    read_input = data0.dt_input  # 原料管以及其分组和编号处理
    tmp_input = []
    raw = []
    for i in range(len(read_input)):
        tmp_input.append(read_input.loc[i].tolist())
    # print(tmp_input)
    for in_p in tmp_input:
        n = int(in_p[1])
        k = n // total_num
        part_sum = 1
        for i in range(k):
            raw.append([[part_sum, part_sum + total_num - 1], in_p[2], total_num, in_p[2]])  # [编号开头（取得到），编号末尾（取不到）]
            part_sum += total_num
        raw.append([[part_sum, part_sum + n - 1 - total_num * k], in_p[2], n - total_num * k, in_p[2]])
    return matrix, product, raw


def initialize(data):
    matrix, product0, raw = read_excel(data)
    product = copy.deepcopy(product0)

    solution = []
    for i in range(40):
        random.shuffle(raw)
        tmp = copy.deepcopy(raw)
        solution.append(tmp)
    s = solution[0]
    s.sort(key=lambda s: s[1], reverse=True)
    for s in solution:
        fit = cal_fitness(s, product, matrix)
        while fit == -1:
            random.shuffle(s)
            fit = cal_fitness(s, product, matrix)
        s.append(fit)
    solution.sort(key=lambda solution: solution[1])
    group = solution
    return group, product0, matrix


def cross(groups, product0, matrix0):
    loc_fitness = len(groups[0]) - 1

    rand = [random.sample((0, len(groups) - 1), 2), random.sample((0, len(groups) - 1), 2)]
    index1 = np.where(groups[rand[0][0]][loc_fitness] < groups[rand[0][1]][loc_fitness], rand[0][0], rand[0][1])
    index2 = np.where(groups[rand[1][0]][loc_fitness] < groups[rand[1][1]][loc_fitness], rand[1][0], rand[1][1])
    parent1 = groups[index1]
    parent2 = groups[index2]

    par1 = copy.deepcopy(parent1)
    par1.pop()
    par2 = copy.deepcopy(parent2)
    par2.pop()
    children = ox(par1, par2)

    index = np.where(random.random() > 0.5, 0, 1)
    children = children[index]

    rand_replace = random.randint(len(groups) // 2, len(groups) - 1)
    groups.sort(key=lambda func: func[loc_fitness])
    groups[rand_replace] = children
    f_c = cal_fitness(children, product0, matrix0)
    groups[rand_replace].append(f_c)
    groups.sort(key=lambda func: func[loc_fitness])

    return groups


def cal_total_num(product_in):
    num = sum([p[0][0][1] for p in product_in])
    return num


def separate_connection(finished_product):
    separate_product = []
    return separate_product


def display_raw(finished_product):  # 用于记录原料管切割情况
    all_raw_part = []
    for fp in finished_product:
        raws = fp[2]
        for r in raws:
            all_raw_part.append(r)
    all_raw_part.sort(key=lambda all_raw_part: all_raw_part[3])
    return all_raw_part


if __name__ == '__main__':
    start = time.time()
    data = initial_data()
    group, product, matrix = initialize(data)
    total_num = sum([p[0][0][1] for p in product])
    for x in range(data.num):
        group = cross(group, product, matrix)
    print(product)
    opt = group[0]
    print(opt)
    opt.pop()
    fit, pro = cal_fitness(opt, product, matrix)
    print("焊点数为%d" % (fit - total_num))
    raw_cut_method = display_raw(pro)
    if data.show_composition:
        [print(p) for p in pro]
    print("此次消耗时间为%f" % (time.time() - start))
