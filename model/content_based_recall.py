#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/3/26 10:11
================================================="""
from __future__ import division
from data_preparation.preprocessing import get_type_percentage, get_avg_type_percentage
import operator


def get_dim_dict(json_list: list, dim_name: str):
    """
    根据指定维度名获取频次字典对象
    :param json_list:
    :param dim_name: 可选category，family，type
    :return:
    """
    if not json_list:
        return {}


def get_up(item_cate: dict, json_list: list):
    """
    用户刻画，即一个rvt文件的特征刻画
    :param item_cate: key：item_id，value：dict，key cate value percent
    :param json_list:
    :return:
    """
    if not json_list:
        return {}
    percent_thr = 0.5  # type percent的阈值
    topk = 10  # 用户最喜欢的类别个数
    record = {}
    up = {}
    for user in json_list:
        user_percentage = get_type_percentage(user)
        user_id = user["project_info"]["FilePath"]+"\\\\"+user["project_info"]["FileName"]  # user_id由路径加文件名生成
        for type_id in user_percentage:
            if user_percentage[type_id] < percent_thr:  # 低于阈值的过滤
                continue
            if type_id not in item_cate:  # item_cate中没有统计的cate也过滤掉
                continue
            if user_id not in record:
                record[user_id] = {}
            for fix_cate in item_cate[type_id]:
                if fix_cate not in record[user_id]:
                    record[user_id][fix_cate] = 0
                record[user_id][fix_cate] += user_percentage[type_id] * item_cate[type_id][fix_cate]
    # 对每个用户喜好的cate进行排序
    for user_id in record:
        if user_id not in up:
            up[user_id] = []
        total_percent = 0
        for c in sorted(record[user_id].items(), key=operator.itemgetter(1), reverse=True)[:topk]:
            up[user_id].append((c[0], c[1]))
            total_percent += c[1]
        for index in range(len(up[user_id])):
            up[user_id][index] = (up[user_id][index][0], round(up[user_id][index][1]/total_percent, 3))  # 用户喜好类别的归一化
    return up


def recom(cate_item_sort: dict, up: dict, user_id, topk=10):
    """

    :param cate_item_sort: reverse sort
    :param up: user profile
    :param user_id: userid to recom
    :param topk: recom num
    :return: a dict, key userid value [item1, item2]
    """
    if user_id not in up:
        return {}
    recom_result = {}
    if user_id not in recom_result:
        recom_result[user_id] = []
    for idx in range(len(up[user_id])-1, 0, -1):
        cate, percent = up[user_id][idx]
        num = int(topk * percent) + 1
        if cate not in cate_item_sort:
            continue
        recom_list = []
        count = 0
        for item in cate_item_sort[cate]:
            if item in recom_result[user_id]:
                continue
            recom_list.append(item)
            count += 1
            if count == num:
                break
        recom_result[user_id] = recom_list + recom_result[user_id]
    return recom_result
