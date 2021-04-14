#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/4/2 11:02
================================================="""
from __future__ import division
from data_preparation.preprocessing import get_type_percentage
import numpy as np
import os
import gensim
import word2vec
import operator

from util import print_run_time


def produce_train_data(data: dict, out_file: str):
    """
    生成item2vec的训练数据
    :param data:
    :param out_file:
    :return:
    """
    if not data:
        return
    percent_thr = 0.5  # type percent的阈值
    record = {}
    for proj_key, proj in data.items():
        proj_percentage = get_type_percentage(proj)
        for type_id in proj_percentage:
            if proj_percentage[type_id] < percent_thr:  # 低于阈值的过滤
                continue
            if proj_key not in record:
                record[proj_key] = []
            record[proj_key].append(type_id)
    fw = open(out_file, "w+")
    for user_id in record:
        fw.write(" ".join(record[user_id]) + "\n")


def cal_type_sim(type_vec, type_id, output_file):
    """
    根据得到的type embedding向量计算type的相似度
    :param type_vec: item embedding vector
    :param type_id: fixed type_id to calc type sim
    :param output_file: the file to store result
    """
    if type_id not in type_vec:
        return
    topk = 10
    score = {}
    fix_type_vec = type_vec[type_id]
    for tmp_type_id in type_vec:
        if tmp_type_id == type_id:
            continue
        tmp_type_vec = type_vec[tmp_type_id]
        denominator = np.linalg.norm(fix_type_vec) * np.linalg.norm(tmp_type_vec)
        if denominator == 0:
            score[tmp_type_id] = 0
        else:
            score[tmp_type_id] = round(np.dot(fix_type_vec, tmp_type_vec) / denominator, 4)
    fw = open(output_file, "a")
    out_str = type_id + "\t"
    tmp_list = []
    for t in sorted(score.items(), key=operator.itemgetter(1), reverse=True)[:topk]:
        tmp_list.append(t[0] + "_" + str(t[1]))
    out_str += ";".join(tmp_list)
    fw.write(out_str + "\n")
    fw.close()


def load_type_vec(type_vec_file):
    """
    加载type embedding向量文件
    :param type_vec_file: file path
    :return: type_vec: a dict, key: type_id, value: np.array[num1, num2, ...] 128 dimension
    有一点问题，不能读取二进制type_vec文件
    """
    if not os.path.exists(type_vec_file):
        return []
    line_num = 0
    type_vec = {}
    fp = open(type_vec_file)
    for line in fp:
        if line_num == 0:
            line_num += 1
            continue
        item = line.strip().split()
        if len(line) < 129:
            continue
        type_id = item[0]
        if type_id == "</s>":
            continue
        type_vec[type_id] = np.array([float(d) for d in item[1:]])
    fp.close()
    return type_vec


@print_run_time
def test_word2vec_main():
    """
    测试Word2Vec模型
    """
    # 初始化参数
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 训练数据路径
    train_data_file = os.path.join(root_path, r"data/train_data.txt")
    # 模型保存路径
    type_vec_file = os.path.join(root_path, r"data/type_vec.txt")
    # 向量聚类结果存储路径，即模型路径
    out_put_clusters = os.path.join(root_path, r"data/output_clusters.txt")

    # 1.生成训练数据文件
    # 2.生成一个bin文件，其中包含二进制格式的单词向量。
    word2vec.word2vec(train_data_file, type_vec_file, size=128, window=5, sample='1e-3', hs=0, negative=5, iter_=100,
                      min_count=1, binary=0, cbow=0, verbose=True)
    # 3.根据训练好的模型对向量进行聚类。这创建了一个txt文件，其中词汇表中的每个单词都有一个集群
    word2vec.word2clusters(train_data_file, out_put_clusters, 100, verbose=True)
    # 4.导入上面创建的word2vec二进制文件
    model = word2vec.load(type_vec_file)
    # 5.查看模型数据
    print("=========Word2Vec=========")
    # #以numpy数组的形式来查看词汇表
    print(model.vocab)
    # #查看整个矩阵
    print(model.vectors.shape)
    print(model.vectors)
    # #检索单个单词的向量
    print("=======================")
    print(model["ca40c8c7-8113-411f-b9ee-7319d9af0090"].shape)
    print(model["ca40c8c7-8113-411f-b9ee-7319d9af0090"][:10])
    # 6.根据余弦相似度进行简单查询，检索与"ca40c8c7-8113-411f-b9ee-7319d9af0090"相似的type:
    indexes, metrics = model.cosine("ca40c8c7-8113-411f-b9ee-7319d9af0090")
    print("=======================")
    print(indexes, metrics)
    print(model.vocab[indexes])
    print(model.generate_response(indexes, metrics))
    print(model.generate_response(indexes, metrics).tolist())
    print("=======================")
    output_file = os.path.join(root_path, r"data/sim_result.txt")
    cal_type_sim(load_type_vec(type_vec_file), "ca40c8c7-8113-411f-b9ee-7319d9af0090", output_file)


@print_run_time
def test_gensim_word2vec_main(data: list):
    """
    测试gensim中Word2Vec模型
    :param data: train data
    :return:
    """
    # 1.生成训练数据文件
    # 2.从文件读取数据
    # 3.训练模型
    new_model = gensim.models.Word2Vec(data, size=128, window=5, min_count=1, sample=1e-3, hs=0, negative=5, iter=100)
    # 4.保存模型
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), r"data/sample_model")
    new_model.save(model_path)
    # 5.从模型文件重载模型
    new_model = gensim.models.Word2Vec.load(model_path)
    # 6.模型测试
    print("=========gensim.models.Word2Vec=========")
    print(new_model.wv.similarity("ca40c8c7-8113-411f-b9ee-7319d9af0090",
                                  "ed2cad60-428b-4708-ae23-9023ebb544bf"))
