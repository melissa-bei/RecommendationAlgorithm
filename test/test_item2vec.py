#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/4/2 11:00
================================================="""
import os
from model.item2vec import test_word2vec_main, test_gensim_word2vec_main
from common.config import Config
from data_preparation.preprocessing import load_datas, produce_train_data, get_type_info


def gen_train_data():
    """
    生成item2vec的训练数据，并写入”../data/train_data.txt“
    """
    data_json_list = load_datas(Config())
    print(len(get_type_info(data_json_list)))
    train_data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), r"data/train_data.txt")
    produce_train_data(data_json_list, train_data_file)


def get_train_data():
    """
    从文件获取训练数据
    :return: 满足gensim.models.Word2Vec格式需求的训练数据
    """
    train_data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), r"data/train_data.txt")
    data = []
    with open(train_data_file, 'r') as f:
        for line in f:
            data.append(list(line.strip('\n').split(' ')))
    return data


def verify_types_num():
    train_data = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), r"data/train_data.txt")
    data = {}
    with open(train_data, 'r') as f:
        for line in f:
            for type_id in list(line.strip('\n').split(' ')):
                if type_id not in data:
                    data[type_id] = 0
                data[type_id] += 1
    print(len(data))
    print(data)
    print("=======================")
    new_data = {}
    for k, v in data.items():
        if v >= 5:
            new_data[k] = v
    print(len(new_data))
    print(new_data)


if __name__ == "__main__":
    # 生成训练数据文件
    # gen_train_data()

    test_word2vec_main()
    test_gensim_word2vec_main(get_train_data())

    # verify_types_num()



