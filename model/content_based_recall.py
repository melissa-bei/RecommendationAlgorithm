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
import numpy as np
from scipy.sparse import coo_matrix


def get_up(item_cate: dict, projs: dict):
    """
    用户刻画，即一个rvt文件的特征刻画
    :param item_cate: key：item_id，value：dict，key cate value percent
    :param projs:
    :return:
    """
    if not projs:
        return {}
    percent_thr: float = 0.5  # type percent的阈值
    topk = 10  # 用户最喜欢的类别个数
    record = {}
    up = {}
    for proj_key, proj in projs.items():
        proj_percentage = get_type_percentage(proj)
        for type_id in proj_percentage:
            if proj_percentage[type_id] < percent_thr:  # 低于阈值的过滤
                continue
            if type_id not in item_cate:  # item_cate中没有统计的cate也过滤掉
                continue
            if proj_key not in record:
                record[proj_key] = {}
            for fix_cate in item_cate[type_id]:
                if fix_cate not in record[proj_key]:
                    record[proj_key][fix_cate] = 0
                record[proj_key][fix_cate] += proj_percentage[type_id] * item_cate[type_id][fix_cate]
    # 对每个proj喜好的cate进行排序
    for proj_key in record:
        if proj_key not in up:
            up[proj_key] = []
        total_percent = 0
        for c in sorted(record[proj_key].items(), key=operator.itemgetter(1), reverse=True)[:topk]:
            up[proj_key].append((c[0], c[1]))
            total_percent += c[1]
        for index in range(len(up[proj_key])):
            up[proj_key][index] = (up[proj_key][index][0], round(up[proj_key][index][1]/total_percent, 3))  # 用户喜好类别的归一化
    return up


def recom(cate_item_sort: dict, up: dict, proj_key, topk=10):
    """
    基于内容和用户标签的推荐
    :param cate_item_sort: reverse sort
    :param up: user profile
    :param proj_key: proj_key to recom
    :param topk: recom num
    :return: a dict, key userid value [item1, item2]
    """
    if proj_key not in up:
        return {}
    recom_result = {}
    if proj_key not in recom_result:
        recom_result[proj_key] = []
    for idx in range(len(up[proj_key])-1, 0, -1):
        cate, percent = up[proj_key][idx]
        num = int(topk * percent) + 1
        if cate not in cate_item_sort:
            continue
        recom_list = []
        count = 0
        for item in cate_item_sort[cate]:
            if item in recom_result[proj_key]:
                continue
            recom_list.append(item)
            count += 1
            if count == num:
                break
        recom_result[proj_key] = recom_list + recom_result[proj_key]
    return recom_result


def recom2(target: np.matrix, m: coo_matrix, types: dict, topk=20):
    """
    给target特征向量进行推荐
    :param target: 目标type的特征向量，可以是m中已有的、也可以是根据标签生成的type，新type的标签必须从已有数据集得到cates中选，目前还不能自定义
    :param m: 数据集中所有type的特征向量
    :param types: 所有type的信息
    :param topk: 推荐结果的个数
    :return recom_list: 包含推荐结果和相关度的字典
    """
    cos_xc = cos_measure(target, m)
    new_order = np.argsort(-cos_xc).tolist()[0]
    type_ids = list(types.keys())
    recom_list = []
    for idy in new_order:
        if (m.getrow(idy).todense() == target).min():  # 过滤推荐列表中的如果由target，则过滤
            continue
        recom_list.append((types[type_ids[idy]], round(cos_xc[0, idy], 3)))
        if len(recom_list) == topk:
            break
    return recom_list


def cos_measure(item_feature_vector, user_rated_items_matrix, rate=0.001):
    """
    计算item之间的余弦夹角相似度
    :param item_feature_vector: 待测量的item特征向量
    :param user_rated_items_matrix: 用户已评分的items的特征矩阵
    :param rate:
    :return: 待计算item与用户已评分的items的余弦夹角相识度的向量
    """
    x_c = (item_feature_vector * user_rated_items_matrix.T) + rate
    mod_x = np.sqrt(item_feature_vector * item_feature_vector.T)
    mod_c = np.sqrt((user_rated_items_matrix * user_rated_items_matrix.T).diagonal())
    cos_xc = x_c / (mod_x * mod_c)

    return cos_xc
