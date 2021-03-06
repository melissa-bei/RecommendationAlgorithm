#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/4/9 15:59
================================================="""
import time


def print_run_time(fn):
    """
    Record the running time of the function
    """
    def inner(*args, **kw):
        start = time.time()
        output = fn(*args, **kw)
        ret = time.time() - start
        if ret < 1e-6:
            unit = "ns"
            ret *= 1e9
        elif ret < 1e-3:
            unit = "us"
            ret *= 1e6
        elif ret < 1:
            unit = "ms"
            ret *= 1e3
        else:
            unit = "s"
        print("Process[%s] total run time is %.1f%s\n" % (fn.__name__, ret, unit))
        return output
    return inner
