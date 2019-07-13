# Created by Gubanov Alexander (aka Derzhiarbuz) at 11.07.2019
# Contacts: derzhiarbuz@gmail.com

import numpy as np
import math
import time
from random import randrange


def tables_mean_square_error(table1, table2):
    if table1.shape != table2.shape:
        return None
    mean_square = 0.
    for i in range(table1.shape[0]):
        for j in range(table1.shape[1]):
            mean_square += (table2[i, j] - table1[i, j]) ** 2
    mean_square /= table1.shape[0] * table1.shape[1]
    return mean_square


def table_probability(table, cols=None, rows=None, n=None):
    if cols is None:
        cols = np.sum(table, axis=0)
    if rows is None:
        rows = np.sum(table, axis=1)
    if n is None:
        n = int(np.sum(cols))
    p = 1.
    for col in cols:
        p *= math.factorial(col)
    p /= math.factorial(n)
    for row in rows:
        p *= math.factorial(row)
    for i in range(cols.size):
        for j in range(rows.size):
            p /= math.factorial(table[i, j])
    return p


def exact_fisher_mc(contingency_table):
    avg = np.zeros(contingency_table.shape)
    cols = np.sum(contingency_table, axis=0)
    rows = np.sum(contingency_table, axis=1)
    n = int(np.sum(cols))
    #calculate probability for given contingency table
    p_treshold = table_probability(contingency_table, cols, rows, n)
    #make arrays for choosing cases during monte carlo procedure
    col_factor_cases = np.zeros(n, dtype=int)
    row_factor_cases = np.zeros(n, dtype=int)
    k = 0
    for i in range(cols.size):
        for j in range(cols[i]):
            col_factor_cases[k] = i
            k += 1
    k = 0
    for i in range(rows.size):
        for j in range(rows[i]):
            row_factor_cases[k] = i
            k += 1
    n_rejected = 0
    max_iter = 10000
    l = 0
    while n_rejected < 50 and l < max_iter:
        #the iteretion of monte-carlo procedure. Independently choose the value for first and second factors for each case
        rand_table = np.zeros(avg.shape, dtype=int)
        for i in range(n):
            k = randrange(n-i)
            p = randrange(n-i)
            rand_table[row_factor_cases[k], col_factor_cases[p]] += 1
            col_factor_cases[p], col_factor_cases[n-i-1] = col_factor_cases[n-i-1], col_factor_cases[p]
            row_factor_cases[k], row_factor_cases[n - i - 1] = row_factor_cases[n - i - 1], row_factor_cases[k]
        p = table_probability(rand_table, cols, rows, n)
        if p <= p_treshold:
            n_rejected += 1
        l += 1
    return n_rejected/l


if __name__ == '__main__':
    arr = np.array([[3, 0, 0], [0, 3, 0], [0, 0, 3]])
    print('true p-value: ' + str(table_probability(arr)*6))
    print('p-value estimation: ' + str(exact_fisher_mc(arr)))
    print('p-value estimation: ' + str(exact_fisher_mc(arr)))
    print('p-value estimation: ' + str(exact_fisher_mc(arr)))
    print('p-value estimation: ' + str(exact_fisher_mc(arr)))