#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/3/26 10:08
================================================="""
# from common.config import Config
from data_preparation.preprocessing import load_datas, get_avg_type_percentage, get_type_cate, get_type_feature, load_type_feature
from data_preparation.generate_datasets import load_dataset
from model.content_based_recall import get_up, recom, recom2, get_type_by_index
import os
import numpy as np
import random

from util import print_run_time


@print_run_time
def test_cbr_main():
    # 基于相似度的推荐
    # 数据预处理
    types, projs, type_fequency = load_dataset()
    # get_type_feature(types)
    m, cates = load_type_feature()
    types_list = list(types.keys())
    out_str = ""
    for idx in range(20):  # random.sample(range(len(types)), 20):  # 取任意20个type进行推荐测试
        # 获取推荐结果
        recom_type_ids = recom2(m.getrow(idx).todense(), m, types)
        # 根据id获取type
        recom_types = get_type_by_index(recom_type_ids, types)
        print("=========target==========")
        print(types[types_list[idx]])
        out_str += "=========target==========\n"
        out_str += "{}\n".format(types[types_list[idx]])
        print("=========recom list==========")
        out_str += "=========recom list==========\n"
        tmp = list(recom_type_ids.keys())
        for idx in range(len(recom_type_ids)):
            sim_score = recom_type_ids[tmp[idx]]
            type = recom_types[idx]
            print(sim_score, type)
            out_str += "{} {}\n".format(sim_score, type)
        print()
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), r"data/cb_recom_result.txt"),
              "w", encoding="utf8") as fw:
        fw.write(out_str)

    # 基于标签的推荐
    # 数据预处理
    # preprocessed_data = load_datas(Config())
    # types, projs = load_dataset()
    # # 获取type的use_percentage
    # avgp = get_avg_type_percentage(projs)
    # for k in types:
    #     if k not in avgp:
    #         print(k + " " + str(types[k]))
    #
    # # 获取type的cate和倒排表
    # item_cate, cate_item_sort = get_type_cate(types, avgp)
    #
    # up = get_up(item_cate, projs)
    # print(len(up))
    #
    # for proj_id in up:
    #     print(up[proj_id])
    #     print("------------recom result--------------")
    #     for item in recom(cate_item_sort, up, proj_id)[proj_id]:
    #         print(item)


if __name__ == "__main__":
    test_cbr_main()
