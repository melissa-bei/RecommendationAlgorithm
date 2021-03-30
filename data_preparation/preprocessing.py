#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2020/9/16 14:21
================================================="""
from __future__ import division
import json
import os
import operator
import re
from common.config import Config


def parse_json(json_name: str, config: Config):
    """
    解析单个自定义导出的json文件，预处理附加信息和项目信息平铺
    :param config: 配置文件类
    :param json_name: 给定json文件路径
    :return json_data:
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
    return json_data


def load_datas(config: Config, num: int = None):
    """
    从资源路径下加载数据集，即文件夹下所有json文件
    :param num: 测试参数，加载前num个json文件
    :param config: 资源路径配置类
    :return datas: [{"project_info":{ }, "type_info":{"id":{ }, ...}, "element_info":{"id":{ }, ...}},...]
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
    for id in parsed_json["element_info"]:
        elem = parsed_json["element_info"][id]
        if elem["CategoryName"] is None or elem["FamilyName"] is None or elem["TypeName"] is None:  # 过滤category、family、type为空的
            continue
        if elem["FamilyType"] not in ["HostObject", "FamilyInstance"]:  # 过滤其他，包含不可见图元以及非常用图元。
            continue
        type_id = elem["TypeId"]  # str(int(elem["TypeId"].split("-")[-1], 16))
        if type_id not in record:
            record[type_id] = 0
        record[type_id] += 1
    return {type_id: round(record[type_id] / len(parsed_json["element_info"]) * 100, 3) for type_id in record}


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
        for id in user["type_info"]:
            type = user["type_info"][id]
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
    type_info = {}
    for user in json_list:
        for id in user["type_info"]:
            type = user["type_info"][id]
            if type["FamilyType"] not in ["HostObject", "FamilyInstance"]:  # 过滤其他，包含不可见图元以及非常用图元。
                continue
            if type["Id"] not in type_info:
                type_info[type["Id"]] = [type["FamilyType"], type["CategoryName"], type["FamilyName"], type["Name"]]
    return type_info


# def get_avg_type_percentage(json_list: list):
# 获取某个类型在项目中的平均使用占比，同96-113行


# ======================================================================================================================
# =====                                                                                                            =====
# ======================================================================================================================
