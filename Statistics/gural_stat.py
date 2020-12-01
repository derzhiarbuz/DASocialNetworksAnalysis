# Created by Gubanov Alexander (aka Derzhiarbuz) at 14.11.2020
# Contacts: derzhiarbuz@gmail.com

import math

def bernoulli_test(n1, n2, p1, two_sided=True):
    pval = .0
    if n1>n2:
        n1,n2 = n2,n1
        p1 = 1. - p1
    N = n1+n2
    p2 = 1. - p1
    if n1>=0:
        pval = pval + p2**N
    print(pval)
    if n1>=1:
        for i in range(1, n1+1):
            perm = 1
            for k in range(1, i+1):
                perm = perm*(N-k+1)/k
            print(perm)
            pval = pval + perm * (p1 ** (i)) * (p2 ** (N-i))
    if two_sided:
        return pval*2
    else:
        return pval


if __name__ == '__main__':
    print(bernoulli_test(20, 22, 0.5, two_sided=True))