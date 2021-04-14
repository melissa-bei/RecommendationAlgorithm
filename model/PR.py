#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/3/30 13:34
================================================="""
from __future__ import division
import operator
import numpy as np
from scipy.sparse.linalg import gmres  # 求解线性方程
from data_preparation.preprocessing import get_graph_from_data, get_type_info, graph_to_m, mat_all_point


def personal_rank(graph, root, alpha, iter_num, recom_num=10):
    """

    :param graph: user item graph
    :param root: the fixed user for which to recom
    :param alpha: the prob to go to random walk
    :param iter_num: iteration num
    :param recom_num: recom item num
    :return: a dict, type_id, value pr
    """
    recom_result = {}
    rank = {}  # 存储所有顶点对于root顶点的pr值
    rank = {point: 0 for point in graph}
    rank[root] = 1
    for iter_idx in range(iter_num):
        tmp_rank = {}
        tmp_rank = {point: 0 for point in graph}
        for out_point, out_dict in graph.items():
            for inner_point, value in graph[out_point].items():
                tmp_rank[inner_point] += round(alpha * rank[out_point] / len(out_dict), 4)
                if inner_point == root:
                    tmp_rank[inner_point] += round(1-alpha, 4)
        if tmp_rank == rank:
            print("Convergent after {} iteration".format(iter_idx))
            break
        rank = tmp_rank
    for item in sorted(rank.items(), key=operator.itemgetter(1), reverse=True):
        point, pr_score = item
        if not point.startswith("type_"):  # 过滤用户顶点
            continue
        if point in graph[root]:  # 过滤用户进行过交互行为的顶点
            continue
        recom_result[point] = round(pr_score, 4)
        if len(recom_result) == recom_num:
            break
    return recom_result


def personal_rank_mat(graph, root, alpha, recom_num=10):
    """

    :param graph: user item graph
    :param root: the fixed user for which to recom
    :param alpha: the prob to go to random walk
    :param recom_num: recom item num
    :return: a dict, type_id, value pr
    """
    m, vertex, address_dict = graph_to_m(graph)
    if root not in address_dict:
        return []
    score_dict = {}
    recom_dict = {}
    mat_all = mat_all_point(m, vertex, alpha)
    idx = address_dict[root]
    r_zero = np.ones((len(vertex), 1))
    res = gmres(mat_all, r_zero, tol=1e-8)[0]
    for idx in range(len(vertex)):
        point = vertex[idx]
        if not point.startswith("type_"):  # 过滤用户顶点
            continue
        if point in graph[root]:  # 过滤用户进行过交互行为的顶点
            continue
        score_dict[point] = round(res[idx], 3)
    for t in sorted(score_dict.items(), key=operator.itemgetter(1), reverse=True)[:recom_num]:
        point, score = t[0], t[1]
        recom_dict[point] = score
    return recom_dict


def get_one_user_recom(types: dict, projs: dict, user: str):
    """
    测试给一个用户进行推荐
    """
    alpha = 0.6
    graph = get_graph_from_data(projs)
    iter_num = 15
    recom_result = personal_rank(graph, user, alpha, iter_num, 100)

    type_info = get_type_info(types, projs)
    for type_id in graph[user]:
        print(type_info[type_id.replace("type_", "")])
    print("------------recom result--------------")
    for type_id in recom_result:
        print(type_info[type_id.replace("type_", "")], recom_result[type_id])
    return recom_result


def get_one_user_recom_by_mat(types: dict, projs: dict, user: str):
    """
    测试给一个用户进行推荐
    """
    alpha = 0.6
    graph = get_graph_from_data(projs)
    recom_result = personal_rank_mat(graph, user, alpha, 100)

    type_info = get_type_info(types, projs)
    for type_id in graph[user]:
        print(type_info[type_id.replace("type_", "")])
    print("------------recom result--------------")
    for type_id in recom_result:
        print(type_info[type_id.replace("type_", "")], recom_result[type_id])
    return recom_result
