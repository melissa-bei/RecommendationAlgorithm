#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/3/26 10:08
================================================="""
import time
import sys
from common.config import Config
from data_preparation.preprocessing import load_datas, get_avg_type_percentage, get_type_cate
from model.content_based_recall import get_up, recom


def main():
    time_start = time.time()

    # 数据预处理
    data_json_list = load_datas(Config())

    # 获取type的use_percentage
    # tp = get_type_percentage(data_json_list[0])
    avgp = get_avg_type_percentage(data_json_list)
    # print(len(avgp))
    # print(avgp["e7740737-f8bf-4b07-a870-a2504a4ea87a-000ae715"])

    # 获取type的cate和倒排表
    item_cate, cate_item_sort = get_type_cate(data_json_list, avgp)
    print(item_cate["e7740737-f8bf-4b07-a870-a2504a4ea87a-000ae715"])
    print(cate_item_sort["HostObject_墙_基本墙"])

    up = get_up(item_cate, data_json_list)
    print(len(up))

    for user_id in up:
        print(up[user_id])
        print("------------recom result--------------")
        for item in recom(cate_item_sort, up, user_id)[user_id]:
            print(item)
    time_end = time.time()
    print('time cost {}s'.format(time_end - time_start))


if __name__ == "__main__":
    main()
