import matplotlib.pyplot as plt
import greedy_solution


def color(x):
    if x == 0:
        return "r"
    elif x == 1:
        return "b"
    elif x == 2:
        return "y"


def check_plot(GS_new):
    ma = greedy_solution.change_solution(GS_new, "yuan")[0:39]
    width = 0.3

    fig, ax = plt.subplots()
    for i in range(len(ma)):
        for j in range(len(ma[i])):

            if j == 0:
                ax.bar(i, ma[i][j][2], width, color=color(ma[i][j][0]))
            elif j == len(ma[i]) - 1:
                ax.bar(i, ma[i][j][1], width, bottom=ma[i][j - 1][2], color=color(ma[i][j][0]))
            else:
                ax.bar(i, ma[i][j][2], width, bottom=ma[i][j - 1][2], color=color(ma[i][j][0]))

    plt.show()
