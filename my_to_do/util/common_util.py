'''
Created on Jan 3, 2018

@author: MTK06979
'''

from bisect import bisect_left


def binary_search(src_ary, target, lo=0, hi=None):
    hi = hi if hi is not None else len(src_ary)
    pos = bisect_left(src_ary, target, lo, hi)
    return (pos if pos != hi and src_ary[pos] == target else -1)
