#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/3/30 14:23
================================================="""
import time
import sys
from __init__ import *
from common.config import Config
from data_preparation.preprocessing import load_datas, get_type_info, graph_to_m, mat_all_point
from model.PR import get_graph_from_data, get_one_user_recom, get_one_user_recom_by_mat


def main():
    time_start = time.time()

    # 数据预处理
    preprocessed_data = load_datas(Config())
    # p = get_graph_from_data(data_json_list)
    # print(p["type_6bfab83c-c282-422e-a6ba-d7c945b382f8-000fcf71"])

    # get_one_user_recom([])
    recom_result_base = get_one_user_recom(preprocessed_data)

    # graph = get_graph_from_data(data_json_list)
    # m, vertex, address_dict = graph_to_m(graph)
    # print(mat_all_point(m, vertex, 0.8))

    recom_result_mat = get_one_user_recom_by_mat(preprocessed_data)

    num = 0
    for elem in recom_result_base:
        if elem in recom_result_mat:
            num += 1
    print(num)

    time_end = time.time()
    print('time cost {}s'.format(time_end - time_start))


if __name__ == "__main__":
    main()
