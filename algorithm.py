import copy
import initial_data
import pandas as pd
import random
from decimal import Decimal


def read_excel(connection=False):
    data = initial_data.initial_data()  # 获得原始数据类，下一步是提取禁接区

    index = list(range(len(data.datatable_output)))  # 生成决定排序的数字顺序index
    random.shuffle(index)
    # change_zone = data.change_zone(index)   # 根据index的顺序将多个管材的禁接区合并
    # matrix = change_zone[0]
    # print(matrix)

    matrix = []  # 将多个禁接列表装在matrix列表中，构成禁接矩阵。
    product = []  # 对原料管的读取和一些准备工作
    read_output = copy.deepcopy(data.datatable_output)
    length = len(read_output)
    tmp_output = []
    for i in range(0, length):
        tmp_output.append(read_output.loc[i].tolist())
        cpy_output = copy.deepcopy(tmp_output)

    if connection:  # 进行原料管虚焊操作
        for i in range(len(index)):
            tmp_output[i] = cpy_output[index[i]][:]
            tmp_output[i].append(index[i])
        cpy_output = copy.deepcopy(tmp_output)
        cpy_output.sort(key=lambda cpy_output: cpy_output[1])
        l = len(tmp_output)
        for j in range(1, l):
            k = j - 1
            add_matrix = data.change_zone(index)[0]
            removed_i = cpy_output[j - 1][-1]
            index.remove(removed_i)
            if j == 1:
                product_num = cpy_output[j - 1][1]
            else:
                product_num = cpy_output[j][1] - cpy_output[j - 1][1]
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
        total_num = 0
        for p in product:
            total_num += p[1]


    else:  # 不进行原料管虚焊操作
        for i in range(len(data.datatable_output)):
            matrix += [data.change_zone([i])[0]]
        for i in range(0, length):
            total_len = Decimal(str(cpy_output[i][2])).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
            product_num = int(tmp_output[i][1])
            product += [
                [[cpy_output[i]], product_num, [], 0, total_len, matrix[i][0][0], matrix[i][0][1], 0, False, [], i]]
        total_num = cal_total_num(product)

    read_input = pd.read_excel('data_input.xlsx', usecols=[0, 1, 2])  # 原料管以及其分组和编号处理
    length = len(read_input)
    tmp_input = []
    raw = []
    for i in range(0, length):
        tmp_input.append(read_input.loc[i].tolist())
    # print(tmp_input)
    for in_p in tmp_input:
        l = in_p[2]
        n = int(in_p[1])
        k = n // total_num
        for i in range(0, k):
            raw.append([i, l, total_num, l])
        raw.append([k, l, n - total_num * k, l])
    # print(raw)

    return matrix, product, raw


def initialize(connection=False):
    matrix, product0, raw = read_excel(connection)
    product = copy.deepcopy(product0)
    # print(matrix)
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


def process(s_in, p, matrix, raw_length, raw_num):
    s = copy.deepcopy(s_in)
    s[2] = raw_num
    temp_length = p[3] + raw_length
    flag = True
    if temp_length <= p[5]:  # 若安装整段原料管不会进入下个禁接区，则直接将其装上去
        p[3] = temp_length
        p[2].append(s)
        p[7] += 1
    elif temp_length >= p[6]:
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
            if temp2[1] >= 500:
                p[9].append(temp2)
        else:  # 未超过全长
            p[3] = temp_length
            p[7] += 1
            for m in matrix:
                if m[0] < temp_length and m[1] > temp_length:
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
                    if temp2[1] >= 500:
                        p[9].append(temp2)
                    break
                if m[0] > temp_length:
                    p[5], p[6] = m[0], m[1]
                    p[2].append(s)
                    break
                if matrix.index(m) == len(matrix) - 1:
                    p[5], p[6] = p[4], p[4]
                    p[2].append(s)
                    break

    else:
        if p[5] == p[3]:
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
        p[9].append(temp2)
    return p


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


def cal_fitness(solution_in, product, matrix, show_composition=False):
    fitness = 0
    solution = copy.deepcopy(solution_in)
    unused_list = []
    flag = True

    for s in solution:
        raw_length = s[1]  # 被研究原料管s的长度
        raw_num = s[2]  # 被研究的原料管s的数量
        for p in product:
            if p[8]:  # 若该产品管已完成，则直接研究下一根产品管
                continue
            if p[5] == p[3] and p[3] + raw_length < p[6]:  # 若目前的原料管受到禁接区约束限制，无法添加到当前研究的产品管是，则直接研究下一根产品管
                continue
            if raw_num >= p[1]:  # 若原料管数量大于当前研究的产品管组，则可在原料管不变的条件下继续到下一根产品管
                raw_num -= p[1]
                temp = p[1]
            elif raw_num == 0:  # 若原料管用完且不缺，则尝试放入下一组原料管
                break
            else:  # 若原料管不足，则需要将当前研究的产品管分为两组，一组全是装上原料管的，另一组全是没有的
                temp = raw_num
                loc = product.index(p)
                copy_p = copy.deepcopy(p)
                copy_p[1] = p[1] - raw_num
                product.insert(loc + 1, copy_p)
                p[1] = temp
                raw_num = 0
            p = process(s, p, matrix[p[-1]], raw_length, temp)  # 具体的原料管安装到产品管的步骤
        if raw_num > 0:  # 若原料管有尚未使用完的，则放入unused list之中备用
            s_copy = copy.deepcopy(s)
            s_copy[2] = raw_num
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
            res_list = merge(res_list)
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

    if show_composition:
        return fitness, product
    else:
        return fitness


def ox(solution1, solution2):
    c1_swap = []
    c2_swap = []

    while True:
        rand1 = random.randint(0, len(solution1) - 1)
        rand2 = random.randint(0, len(solution1) - 1)
        min_rand = min(rand1, rand2)
        max_rand = max(rand1, rand2)
        if min_rand < max_rand:
            break
    # print(min_rand)
    # print(max_rand)

    copy1 = solution1[min_rand:max_rand + 1]
    copy2 = solution2[min_rand:max_rand + 1]
    s1_head = solution1[:min_rand]
    s1_head.reverse()
    s1_tail = solution1[max_rand + 1:]
    s1_tail.reverse()
    s2_head = solution2[:min_rand]
    s2_head.reverse()
    s2_tail = solution2[max_rand + 1:]
    s2_tail.reverse()
    swap2 = s1_head + s1_tail  # 编号没错
    swap1 = s2_head + s2_tail  # 编号没错

    while swap1:
        tmp = swap1.pop()
        if tmp not in copy1:
            c1_swap.append(tmp)
    for c in copy2:
        if c not in copy1:
            c1_swap.append(c)
    c1 = c1_swap[len(solution1) - max_rand - 1:] + copy1 + c1_swap[:len(solution1) - max_rand - 1]

    while swap2:
        tmp = swap2.pop()
        if tmp not in copy2:
            c2_swap.append(tmp)
    for c in copy1:
        if c not in copy2:
            c2_swap.append(c)
    c2 = c2_swap[len(solution2) - max_rand - 1:] + copy2 + c2_swap[:len(solution2) - max_rand - 1]

    return c1, c2


def cross(group, product0, matrix):
    product = copy.deepcopy(product0)
    groups = copy.deepcopy(group)

    loc_fitness = len(groups[0]) - 1
    rand1 = random.randint(0, len(groups) - 1)
    rand2 = rand1
    while rand2 == rand1:
        rand2 = random.randint(0, len(groups) - 1)
    if groups[rand1][loc_fitness] < groups[rand2][loc_fitness]:
        parent1 = groups[rand1]
    else:
        parent1 = groups[rand2]
    rand3 = random.randint(0, len(groups) - 1)
    rand4 = rand3
    while rand3 == rand4:
        rand4 = random.randint(0, len(groups) - 1)
    if groups[rand3][loc_fitness] < groups[rand4][loc_fitness]:
        parent2 = groups[rand3]
    else:
        parent2 = groups[rand4]

    par1 = copy.deepcopy(parent1)
    par1.pop()
    par2 = copy.deepcopy(parent2)
    par2.pop()
    children1, children2 = ox(par1, par2)
    rand = random.random()
    if rand > 0.5:
        children = children1
    else:
        children = children2
    # print(children)

    rand_replace = random.randint(len(groups) // 2, len(groups) - 1)
    groups.sort(key=lambda groups: groups[loc_fitness])
    groups[rand_replace] = children
    f_c = cal_fitness(children, product, matrix)
    groups[rand_replace].append(f_c)
    groups.sort(key=lambda groups: groups[loc_fitness])

    return groups


def cal_total_num(product_in):
    num = 0
    for p in product_in:
        num += p[0][0][1]
    return num


if __name__ == '__main__':
    group, product, matrix = initialize(connection=False)
    total_num = cal_total_num(product)
    num = 1000
    for i in range(0, num):
        group = cross(group, product, matrix)
    print(product)
    # for g in group:
    #     print(g[-1])
    opt = group[0]
    print(opt)
    opt.pop()
    fit, pro = cal_fitness(opt, product, matrix, show_composition=True)
    print(fit - total_num)
    for p in pro:
        print(p)
