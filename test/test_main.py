#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2020/9/16 14:21
================================================="""
import time

from common.config import Config
from data_preparation.preprocessing import load_datas, get_type_percentage, get_avg_type_percentage, get_type_cate
from content_based_rec.content_based_recall import get_up, recom


def main():
    time_start = time.time()

    resource_dir = "E:/cbim_revit_batch/resource"
    # 数据预处理
    data_json_list = load_datas(Config(resource_dir), 1)

    # 获取type的use_percent
    # tp = get_type_percent(data_json_list[0])
    avgp = get_avg_type_percentage(data_json_list)
    # print(len(avgp))
    # print(avgp["e7740737-f8bf-4b07-a870-a2504a4ea87a-000ae715"])

    # 获取type的cate和倒排表
    item_cate, cate_item_sort = get_type_cate(data_json_list, avgp)
    print(item_cate["e7740737-f8bf-4b07-a870-a2504a4ea87a-000ae715"])
    print(cate_item_sort["HostObject_墙_基本墙"])

    up = get_up(item_cate, data_json_list)
    print(len(up))
    user_id = "E:\\\\cbim_revit_batch\\\\resource\\\\exportedjson\\\\02\\ 清华大学深圳国际校区\\\\02-初步设计\\\\02-建筑\\\\20190122建筑提图\\\\B座\\\\18172-B-AR&ST-F1~RF-center_A-yanxt_0122提资（房间名称更新）"
    print(up[user_id])

    for item in recom(cate_item_sort, up, user_id)[user_id]:
        print(item)
    time_end = time.time()
    print('time cost {}s'.format(time_end - time_start))


if __name__ == "__main__":
    main()
