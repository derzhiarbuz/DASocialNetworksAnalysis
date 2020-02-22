# Created by Gubanov Alexander (aka Derzhiarbuz) at 18.02.2020
# Contacts: derzhiarbuz@gmail.com

import matplotlib.pyplot as plt
import numpy as np
import math

def show_likelyhood_heatmap2D(x, y, z, true, est, xlabel='x', ylabel='y', exp = False):
    xs, ys = np.meshgrid(x, y)
    if exp:
        zz = z.copy()
        max = -1e20
        for i in range(len(xs)):
            for j in range(len(ys)):
                if z[i][j] > max:
                    max = z[i][j]
        max -= 300
        for i in range(len(xs)):
            for j in range(len(ys)):
                if z[i][j] >= max:
                    zz[i][j] = math.exp(z[i][j] - max)
                else:
                    zz[i][j] = .0
    else:
        zz = z
    plt.figure(figsize=(5, 5))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.contourf(xs, ys, zz.transpose(), levels=15)
    plt.scatter([est[0]], [est[1]], color='blue', marker='+')
    plt.scatter([true[0]], [true[1]], color='red', marker='o')
    plt.show()