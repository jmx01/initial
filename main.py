from generate_function import sequence_decode
from greedy_solution import greedy_solve


def main():
    initial = []  # 生成64个初始解，1个贪婪解，63个随机解

    GS = greedy_solve()

    if GS.material_length >= GS.product_length:
        # 贪婪解
        count = 0
        while count < GS.greedy_solution_quantity:
            GS_new, t_greedy, team, weld = GS.solve_1()  # 新生成的贪婪解
            if GS_new != 10 and GS_new != 111 and GS_new not in initial:
                initial.append(GS_new)
                count += 1
                print("焊点数为%d" % weld)
                print("贪婪解耗时%d" % t_greedy)
            elif GS_new == 10:
                print("生成超时，建议更换算法")
            elif GS_new == 111:
                print("错误警告，原料管用光")
            else:
                print("GS_new生成出错，生成新的初始解")

        return initial  # 返回初始解的集

    else:
        print("原料过少，无法套管")
        return 110


# if __name__ == "main":
main()
