#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/3/30 14:23
================================================="""
# from common.config import Config
from data_preparation.preprocessing import load_datas, get_type_info, graph_to_m, mat_all_point
from model.PR import get_graph_from_data, get_one_user_recom, get_one_user_recom_by_mat
from data_preparation.generate_datasets import load_dataset
from util import print_run_time


@print_run_time
def test_pr_main():
    # 数据预处理
    # preprocessed_data = load_datas(Config())
    types, projs = load_dataset()

    user = next(iter(projs.keys()))
    print(user)
    recom_result_base = get_one_user_recom(types, projs, user)

    # graph = get_graph_from_data(data_json_list)
    # m, vertex, address_dict = graph_to_m(graph)
    # print(mat_all_point(m, vertex, 0.8))

    recom_result_mat = get_one_user_recom_by_mat(types, projs, user)

    num = 0
    for elem in recom_result_base:
        if elem in recom_result_mat:
            num += 1
    print(num)


if __name__ == "__main__":
    test_pr_main()
