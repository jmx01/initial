from greedy_solution import greedy_solve
from generate_function import sequence_decode


def main():
    initial = []  # 生成64个初始解，1个贪婪解，63个随机解

    GS = greedy_solve()
    GS_new = GS.solve()  #
    c = sequence_decode(GS_new[0], GS_new[1], GS.no_pick_zone)  #

    if GS.material_length >= GS.product_length:
        # 贪婪解
        count = 0
        while count < GS.greedy_solution_quantity:
            GS_new = GS.solve()  # 新生成的贪婪解
            if GS_new != 0 and GS_new != 1 and GS_new not in initial:
                initial.append(GS_new)
                # plot_use_file.check_plot(GS_new)
                count += 1
            else:
                print("GS_new生成出错，生成新的初始解")

        return initial  # 返回初始解的集

    else:
        print("原料过短，无法套管")
        return 0


main()
