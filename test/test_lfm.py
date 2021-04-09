#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/3/29 14:35
================================================="""
import time
import sys
from __init__ import *
from common.config import Config
from data_preparation.preprocessing import load_datas, get_type_info, get_avg_type_percentage
from model.LFM import get_train_data, lfm_train_func, get_recom_result, ana_recom_result


def model_train_process():
    """
    test lfm model train
    """
    preprocessed_data = load_datas(Config())
    train_data = get_train_data(preprocessed_data)
    user_vec, type_vec = lfm_train_func(train_data, 50, 0.01, 0.1, 50)
    # print(user_vec, type_vec)
    for proj_key in preprocessed_data:
        print(proj_key)
        recom_list = get_recom_result(user_vec, type_vec, proj_key)
        # print(recom_list)
        ana_recom_result(preprocessed_data, train_data, proj_key, recom_list)


def test_main():
    time_start = time.time()

    # 数据预处理
    preprocessed_data = load_datas(Config())

    # # 获取item信息
    # item_info = get_type_info(preprocessed_data)
    # print(len(item_info))
    # print([item_info.get(k) for k in list(item_info.keys())[:10]])
    #
    # # 获取用户对item的平均打分
    # avgp = get_avg_type_percentage(preprocessed_data)
    # print(len(avgp))
    # print(avgp["d5bed3a8-22e6-4a2c-a2a3-efdbc032cd3f-0012cba0"])

    train_data = get_train_data(preprocessed_data)
    print(len(train_data))
    print(train_data[:50])

    time_end = time.time()
    print('time cost {}s'.format(time_end - time_start))


if __name__ == "__main__":
    # test_main()
    model_train_process()
