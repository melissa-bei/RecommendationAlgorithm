#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/3/24 11:14
================================================="""
from __future__ import division
import json
import os
import operator
import re
from scipy.sparse import coo_matrix
import numpy as np
from common.config import Config


def parse_json(json_name: str, config: Config):
    """
    解析单个自定义导出的json文件，预处理附加信息和项目信息平铺
    :param config: 配置文件类
    :param json_name: 给定json文件路径
    :return type_info: A dict，推荐对象的信息
            element_info: A dict，项目与推荐对象的交互信息，即一个项目使用了多少次某个type
    """
    json_data = json.load(open(json_name, encoding="utf8"))
    # 添加更新项目信息
    json_data = config.update_proj_info(json_data)

    # 将项目信息平铺到图元
    for id, element in json_data["element_info"].items():
        element["FileName"] = json_data["project_info"]["FileName"]
        element["FilePath"] = json_data["project_info"]["FilePath"]
        # element["Elevation"] = json_data["project_info"]["Elevation"]
        element["Address"] = (float(json_data["project_info"]["Latitude"]), float(json_data["project_info"]["Longitude"]))
        element["PlaceName"] = json_data["project_info"]["PlaceName"]
        element["TimeZone"] = json_data["project_info"]["TimeZone"]
        # element["OrganizationDescription"] = json_data["project_info"]["OrganizationDescription"]
        # element["OrganizationName"] = json_data["project_info"]["OrganizationName"]
        element["Author"] = json_data["project_info"]["Author"]
        element["Number"] = json_data["project_info"]["Number"]
        element["OwnerProject"] = json_data["project_info"]["Name"]
        element["ClientName"] = json_data["project_info"]["ClientName"]
        element["Status"] = json_data["project_info"]["Status"]
        # element["IssueDate"] = json_data["project_info"]["IssueDate"]
        element["Status"] = json_data["project_info"]["Status"]
        element["BuildingType"] = json_data["project_info"]["BuildingType"]
        element["Major"] = json_data["project_info"]["Major"]

        json_data["element_info"][id] = element
    return json_data["type_info"], json_data["element_info"]


def load_datas(config: Config, num: int = None):
    """
    从资源路径下加载数据集，即文件夹下所有json文件
    :param num: 测试参数，加载前num个json文件
    :param config: 资源路径配置类
    :return datas: [({"id":{ }, ...}->"type_info", {"id":{ }, ...}}->"element_info"),...]
    """
    datas = []
    count = 0
    for root, dirs, files in os.walk(config.json_dir):
        for file in files:
            if file.endswith(".json"):
                count += 1
                datas.append(parse_json(os.path.join(root, file), config))
            if count == num:
                return datas
    return datas


# ======================================================================================================================
# 问题出在了用户的刻画上，需要规范好推荐的输入的参数，比如给定专业、建筑类型、某个category、某个family、某个type、某个关键词之类的，这些参数可有可无。
# 一是说我要通过给定一些参数去描述一个新的用户（也即是一个新的Revit项目），根据这些关键词如推荐一些某个family、type给我的用户，
#    这种情况就直接根据一些标签查表去返回topk的对象
# 二是说通过当前检索页面中所展示的图元的一些属性来推荐一些family、type给到当前用户。这一过程主要需要的是构建type之间的关联性和相似度，
#    这种情况需要具体的某个图元获取一些标签，然后查表返回topk的对象
# 总的来说，输入信息可以简要的定义为目前图元所包含的一些字段。
# 目前看的content-based和LFM都是根据已有的数据建立了user profile，在预测时也只针对表中已有的用户才能去做推荐，也就是将用户提炼得到用户up，
#     然后根据用户id去获取up，再由up中的标签去查表然后进行推荐。由此分析，想要完成根据一些关键词的推荐，就需要弱化用户up的概念，去直接根据关键词
#     获取推荐的对象列表。
# 因此，需要考虑的一个问题是如何构建用户up，以便于后期去掉不影响推荐流程。目前根据每个type再单个rvt文件中的使用率和category、family、type
#     生成的标签来构建用户up、type_info是有问题的，可能是标签权重设计的问题，这样处理后推荐系统输入的对象也就是极度依赖于这些标签，
#     并不是一个理想的处理方法。
# ======================================================================================================================


def get_type_percentage(parsed_json: dir):
    """
    由解析后的json获取当前rvt文件的各个type的使用率
    :param parsed_json:
    :return: A dict，key；type_id，value：percentage * 100
    """
    if not parsed_json:
        return {}

    record = {}
    for id in parsed_json[1]:
        elem = parsed_json[1][id]
        if elem["CategoryName"] is None or elem["FamilyName"] is None or elem["TypeName"] is None:  # 过滤category、family、type为空的
            continue
        if elem["FamilyType"] not in ["HostObject", "FamilyInstance"]:  # 过滤其他，包含不可见图元以及非常用图元。
            continue
        type_id = elem["TypeId"]  # str(int(elem["TypeId"].split("-")[-1], 16))
        if type_id not in record:
            record[type_id] = 0
        record[type_id] += 1
    return {type_id: round(record[type_id] / len(parsed_json[1]) * 100, 3) for type_id in record}


# ======================================================================================================================
# =====                                    Content based recall                                                    =====
# ======================================================================================================================
def get_avg_type_percentage(json_list: list):
    """
    获取某个类型在项目中的平均使用占比
    :param json_list:
    :return:
    """
    if not json_list:
        return {}

    record = {}
    for user in json_list:
        user_percentage = get_type_percentage(user)
        for type_id in user_percentage:
            if type_id not in record:
                record[type_id] = [0, 0]
            record[type_id][0] += user_percentage[type_id]
            record[type_id][1] += 1
    return {type_id: round(record[type_id][0] / record[type_id][1], 3) for type_id in record}


def get_type_cate(json_list: list, avg_type_percentage: dict):
    """
    获取type的相关标签，包含category、family、type
    hostobject属性都在name中
    familyinstance属性在familyname和type中
    主要以“_”和“-”做切分。
    other属性也取familyname和type中

    注：没有type的过滤掉
    :param avg_type_percentage:
    :param json_list:
    :return:
    """
    if not json_list:
        return {}
    topk = 100  # 取每个标签下的前topk个type（item）
    item_cate = {}
    record = {}
    cate_item_sort = {}
    for user in json_list:
        for id in user[0]:
            type = user[0][id]
            if type["CategoryName"] is None or type["FamilyName"] is None or type["Name"] is None:  # 过滤category、family、type为空的
                continue

            if type["FamilyType"] == "HostObject":  # 系统族
                _tmp = list(map(str.strip, re.split(r"[_-]", type["Name"])))
                cate_list = [type["FamilyType"] + "_" + type["CategoryName"] + "_" + type["FamilyName"]] + _tmp
                # ratios = [1 / 4, 1 / 4, 1 / 4] + len(_tmp) * [1 / 4 / len(_tmp)]
                ratios = [round(1 / len(cate_list), 3)] * len(cate_list)

            elif type["FamilyType"] == "FamilyInstance":  # 载入族、内建族
                _tmp1 = list(map(str.strip, re.split(r"[_-]", type["FamilyName"])))
                _tmp2 = list(map(str.strip, re.split(r"[_-]", type["Name"])))
                cate_list = [type["FamilyType"] + "_" + type["CategoryName"]] + _tmp1 + _tmp2
                # ratios = [1 / 4, 1 / 4] + len(_tmp1) * [1 / 4 / len(_tmp1)] + len(_tmp2) * [1 / 4 / len(_tmp2)]
                ratios = [round(1 / len(cate_list), 3)] * len(cate_list)

            else:  # 过滤其他，包含不可见图元以及非常用图元。导致item_cate比json文件中的type_info少了一些
                continue
            # if typeid not in item_cate:
            #     item_cate[typeid] = {}
            # for idx in range(len(cate_list)):
            #     item_cate[typeid][cate_list[idx]] = ratios[idx]
            if type["Id"] not in item_cate:
                item_cate[type["Id"]] = {}
            for idx in range(len(cate_list)):
                item_cate[type["Id"]][cate_list[idx]] = ratios[idx]

    # 获取每个cate下item的avg_percent
    for typeid in item_cate:
        for cate in item_cate[typeid]:
            if cate not in record:
                record[cate] = {}
            record[cate][typeid] = avg_type_percentage.get(typeid, 0)  # 每个cate下每个type的平均percent

    # 排序并装载
    for cate in record:
        if cate not in cate_item_sort:
            cate_item_sort[cate] = []
        for c in sorted(record[cate].items(), key=operator.itemgetter(1), reverse=True)[:topk]:
            cate_item_sort[cate].append(c[0] + "_" + str(c[1]))

    return item_cate, cate_item_sort


# ======================================================================================================================
# =====                                            LFM                                                             =====
# ======================================================================================================================
def get_type_info(json_list: list):
    """
    获取type的信息
    :param json_list:
    :return:
    """
    if not json_list:
        return {}
    percent_thr = 0.5
    type_info = {}
    for user in json_list:
        user_percentage = get_type_percentage(user)
        for id in user[0]:
            type = user[0][id]
            if type["FamilyType"] not in ["HostObject", "FamilyInstance"]:  # 过滤其他，包含不可见图元以及非常用图元。
                continue
            if type["CategoryName"] is None or type["FamilyName"] is None or type["Name"] is None:  # 过滤category、family、type为空的
                continue
            if type["Id"] not in type_info:
                type_info[type["Id"]] = [type["FamilyType"], type["CategoryName"], type["FamilyName"], type["Name"]]
            if user_percentage[type["Id"]] < percent_thr:  # 使用率低于阈值过滤
                continue
    return type_info


# def get_avg_type_percentage(json_list: list):
# 获取某个类型在项目中的平均使用占比，同96-113行


# ======================================================================================================================
# =====                                            PR                                                              =====
# ======================================================================================================================
def get_graph_from_data(json_list: list):
    """
    从数据中构建二分图
    :param json_list:
    :return:  a dict: {user1:{item1:1, item2:1}, item1:{user1:1, user2:1}}
    """
    if not json_list:
        return {}
    percent_thr = 0.5
    graph = {}

    for user in json_list:
        if len(user[0]) == 0:  # 过滤掉type为空的user，即该user没有对推荐按列表中的任何type进行过行为，比如红线、轴网类型的rvt文件
            continue
        _, tmp_elem = next(iter(user[1].items()))
        user_id = tmp_elem["FilePath"] + "\\\\" + tmp_elem["FileName"]
        user_percentage = get_type_percentage(user)
        if user_id not in graph:
            graph[user_id] = {}
        for id in user[0]:
            type = user[0][id]
            if type["CategoryName"] is None or type["FamilyName"] is None or type["Name"] is None:  # 过滤category、family、type为空的
                continue
            if type["FamilyType"] not in ["HostObject", "FamilyInstance"]:  # 过滤其他，包含不可见图元以及非常用图元。
                continue
            if user_percentage[type["Id"]] < percent_thr:  # 使用率低于阈值过滤
                continue
            type_id = "type_" + type["Id"]
            graph[user_id][type_id] = 1
            if type_id not in graph:
                graph[type_id] = {}
            graph[type_id][user_id] = 1

    # score_thr = 4.0
    # linenum = 0
    # fp = open("../data_preparation/PR_sample.txt")
    # for line in fp:
    #     if linenum == 0:
    #         linenum += 1
    #         continue
    #     item = line.strip().split(",")
    #     if len(item) < 3:
    #         continue
    #     user_id, type_id, rating = item[0], "type_" + item[1], item[2]
    #     if float(rating) < score_thr:
    #         continue
    #     if user_id not in graph:
    #         graph[user_id] = {}
    #     graph[user_id][type_id] = 1
    #     if type_id not in graph:
    #         graph[type_id] = {}
    #     graph[type_id][user_id] = 1
    # fp.close()
    return graph


# def get_type_info(json_list: list):
# 获取type的信息，同203-219行


def graph_to_m(graph: dict):
    """
    由dict类型的graph转为矩阵
    :param graph: user item graph
    :return: a coo_matrix, sparse mat M;
             a list, total user item point;
             a dict, map all point to row index;
    """
    vertex = list(graph.keys())
    address_dict = {}
    for idx in range(len(vertex)):
        address_dict[vertex[idx]] = idx
    row = []
    col = []
    data = []
    for elemi in graph:
        weight = round(1/len(graph[elemi]), 3)
        row_idx = address_dict[elemi]
        for elemj in graph[elemi]:
            col_idx = address_dict[elemj]
            row.append(row_idx)
            col.append(col_idx)
            data.append(weight)
    row = np.array(row)
    col = np.array(col)
    data = np.array(data)
    m = coo_matrix((data, (row, col)), shape=(len(vertex), len(vertex)))
    return m, vertex, address_dict


def mat_all_point(m_mat: coo_matrix, vertex: list, alpha: float):
    """
    获取E-alpha*m_mat.T
    :param m_mat:
    :param vertex: total user and item point
    :param alpha: the prob for random walking
    :return:
    """
    total_len = len(vertex)
    row = np.array(range(total_len))
    col = np.array(range(total_len))
    data = np.ones(total_len)
    eye_t = coo_matrix((data, (row, col)), shape=(total_len, total_len))
    print(eye_t.todense())
    return eye_t.tocsr() - alpha * m_mat.tocsr().transpose()


# ======================================================================================================================
# =====                                        item2vec                                                            =====
# ======================================================================================================================
def produce_train_data(json_list: list, out_file: str):
    """
    生成item2vec的训练数据
    :param json_list:
    :param out_file:
    :return:
    """
    if not json_list:
        return
    percent_thr = 0.5  # type percent的阈值
    record = {}
    for user in json_list:
        user_percentage = get_type_percentage(user)
        _, tmp_elem = next(iter(user[1].items()))
        user_id = tmp_elem["FilePath"] + "\\\\" + tmp_elem["FileName"]
        for type_id in user_percentage:
            if user_percentage[type_id] < percent_thr:  # 低于阈值的过滤
                continue
            if user_id not in record:
                record[user_id] = []
            record[user_id].append(type_id)
    fw = open(out_file, "w+")
    for user_id in record:
        fw.write(" ".join(record[user_id]) + "\n")
    fw.close()
