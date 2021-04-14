#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/3/29 15:04
================================================="""
import operator
import numpy as np
from data_preparation.preprocessing import get_type_percentage, get_avg_type_percentage


def get_train_data(projs: dict):
    """
    为LFM模型准备训练数据
    :param projs:
    :return: a list:[(user_id, item_id, label), ……], label is 1 or 0
    """
    if not projs:
        return {}
    neg_dict = {}
    pos_dict = {}
    train_data = []
    percent_thr = 0.2
    # 获取用户对item的平均打分
    avgp = get_avg_type_percentage(projs)
    for proj_key, proj in projs.items():
        proj_percentage = get_type_percentage(proj)
        if proj_key not in pos_dict:
            pos_dict[proj_key] = []
        if proj_key not in neg_dict:
            neg_dict[proj_key] = []
        for type_id in proj_percentage:
            if proj_percentage[type_id] > percent_thr:  # 使用率高于阈值为正样本
                pos_dict[proj_key].append((type_id, 1))
            else:
                percent = avgp.get(type_id, 0)  # 使用率低于于阈值为负样本
                neg_dict[proj_key].append((type_id, percent))
    # 正负样本的均衡：负采样
    for user_id in pos_dict:
        data_num = min(len(pos_dict[user_id]), len(neg_dict.get(user_id, [])))
        if data_num > 0:
            train_data += [(user_id, item[0], item[1]) for item in pos_dict[user_id]][:data_num]
            sorted_neg_list = sorted(neg_dict[user_id], key=operator.itemgetter(1), reverse=True)[:data_num]
            train_data += [(user_id, item[0], 0) for item in sorted_neg_list]
    return train_data


def init_vec(vector_len):
    """
    初始化向量
    :param vector_len: the len of vector
    :return: a ndarray
    """
    return np.random.randn(vector_len)


def model_predict(user_vector, type_vector):
    """
    预测用户和某个type之间的距离
    :param user_vector: 模型生成的用户向量
    :param type_vector: 模型生成的type的向量
    :return:
    """
    return np.dot(user_vector, type_vector)/(np.linalg.norm(user_vector) * np.linalg.norm(type_vector))


def lfm_train_func(train_data, F, alpha, beta, step):
    """
    lfm的训练函数
    :param train_data: 训练样本
    :param F: 用户向量和item向量的维度
    :param alpha: 正则化参数
    :param beta: 学习率 learning rate
    :param step: 迭代次数
    :return: dict: key item_id, value np.ndarray, the vector of item
             dict: key user_id, value np.ndarray, the vector of user
    """
    user_vec = {}
    type_vec = {}
    loss = 0
    for step_idx in range(step):
        for data_instance in train_data:
            user_id, type_id, label = data_instance

            if user_id not in user_vec:
                user_vec[user_id] = init_vec(F)
            if user_id not in type_vec:
                type_vec[type_id] = init_vec(F)
            pred = model_predict(user_vec[user_id], type_vec[type_id])
            loss += label-pred
        user_vec[user_id] += beta * ((loss / F) * type_vec[type_id] - alpha * user_vec[user_id])
        type_vec[type_id] += beta * ((loss / F) * user_vec[user_id] - alpha * type_vec[type_id])
        beta *= 0.9
    return user_vec, type_vec


def get_recom_result(user_vec, type_vec, user_id):
    """

    :param user_vec: lfm model result
    :param type_vec: lfm model result
    :param user_id:
    :return: a list: [(item_id, score),……]
    """
    if user_id not in user_vec:
        return []
    fix_num = 10
    record = {}
    recom_list = []
    user_vector = user_vec[user_id]
    for type_id in type_vec:
        type_vector = type_vec[type_id]
        res = model_predict(user_vector, type_vector)
        record[type_id] = res
    for t in sorted(record.items(), key=operator.itemgetter(1), reverse=True)[:fix_num]:
        type_id, score = t
        recom_list.append((type_id, score))
    return recom_list


def ana_recom_result(type_info, train_data, user_id, recom_list):
    """
    评估推荐结果
    :param type_info:
    :param train_data:
    :param user_id:
    :param recom_list:
    """
    print("prefer_list")
    for data_instance in train_data:
        if data_instance[0] == user_id:
            _, type_id, label = data_instance
            if label == 1:
                print([type_id] + type_info[type_id])
    print("recom_list")
    for c in recom_list:
        print([c[0]] + type_info[c[0]])
