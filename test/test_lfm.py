#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/3/29 14:35
================================================="""
# from common.config import Config
from data_preparation.preprocessing import get_type_info
from data_preparation.generate_datasets import load_dataset
from model.LFM import get_train_data, lfm_train_func, get_recom_result, ana_recom_result

from util import print_run_time


@print_run_time
def test_lfm_main():
    """
    test lfm model train
    """
    types, projs, _ = load_dataset()

    train_data = get_train_data(projs)
    user_vec, type_vec = lfm_train_func(train_data, 50, 0.01, 0.1, 50)
    # print(user_vec, type_vec)

    type_info = get_type_info(types, projs)
    for proj_key in projs:
        print(proj_key)
        recom_list = get_recom_result(user_vec, type_vec, proj_key)
        # print(recom_list)
        ana_recom_result(type_info, train_data, proj_key, recom_list)


@print_run_time
def test_get_train_data_main():
    # 数据预处理
    # preprocessed_data = load_datas(Config())
    types, projs = load_dataset()

    # 获取item信息
    type_info = get_type_info(types, projs)
    print(len(type_info))
    print([type_info.get(k) for k in list(type_info.keys())[:10]])

    train_data = get_train_data(projs)
    print(len(train_data))
    print(train_data[:50])


if __name__ == "__main__":
    # test_get_train_data_main()
    test_lfm_main()
