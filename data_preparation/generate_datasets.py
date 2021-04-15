#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/4/12 11:17
================================================="""
from common.config import Config
import os
import json
import re
import uuid
from util import print_run_time


def parse_json(json_name: str, config: Config):
    """
    解析单个自定义导出的json文件，预处理附加信息和项目信息平铺。对于无效的type、element进行清洗。
    :param config: 配置文件类
    :param json_name: 给定json文件路径
    :return {"type": A dict，推荐对象的信息, "element": A list，项目与推荐对象的交互信息，即一个项目使用了多少次某个type}
    """
    json_data = json.load(open(json_name, encoding="utf8"))

    # 添加更新项目信息
    json_data = config.update_proj_info(json_data)

    # 对proj进行数据清洗
    new_proj_info = {}
    field_list = ["Name", "BuildingType", "Status", "Major"]
    for f in field_list:
        new_proj_info[f] = json_data["project_info"][f]

    # 对type进行数据清洗
    new_type_infos = []
    for type in json_data["type_info"].values():
        if type["CategoryName"] is None or\
           type["FamilyName"] is None or\
           type["Name"] is None:  # 过滤category、family、type为空的
            continue
        if type["FamilyType"] not in ["HostObject", "FamilyInstance", "Other"]:  # 过滤其他，包含不可见图元以及非常用图元，如红线、轴网类型等无效type。
            continue
        if type["FamilyName"] == "导入符号"or type["Category"].isdigit() or \
           type["Category"] == "OST_RvtLinks" or type["Category"] == "OST_Entourage" or\
           type["Category"] == "OST_Planting" or type["Category"] == "OST_Site" or\
           type["Category"] == "OST_Mass":
            continue
        new_type_infos.append(type)

    # 对element进行数据清洗
    new_element_infos = []
    for _, element in json_data["element_info"].items():
        if element["CategoryName"] is None or\
           element["FamilyName"] is None or\
           element["TypeName"] is None:  # 过滤category、family、type为空的
            continue
        if element["FamilyType"] not in ["HostObject", "FamilyInstance", "Other"]:  # 过滤其他，包含不可见图元以及非常用图元。
            continue
        if element["FamilyName"] == "导入符号"or element["Category"].isdigit() or \
           element["Category"] == "OST_RvtLinks" or element["Category"] == "OST_Entourage" or\
           element["Category"] == "OST_Planting" or element["Category"] == "OST_Site" or\
           element["Category"] == "OST_Mass":
            continue
        element.pop("Category")
        element.pop("CategoryName")
        element.pop("FamilyId")
        element.pop("FamilyName")
        element.pop("FamilyType")
        element.pop("TypeName")
        element.pop("Name")
        new_element_infos.append(element)
    if new_type_infos and new_element_infos:
        return {"project": new_proj_info, "type": new_type_infos, "element": new_element_infos}
    else:
        return


def load_raw_data(config: Config, num: int = 100):
    """
    从资源路径下加载数据集，即文件夹下所有json文件，将属于同一个项目下的所有rvt中的type和图元合并起来
    :param num: 测试参数，加载前num个json文件
    :param config: 资源路径配置类
    :return datas: {"proj1": {"type": [type1, ...], "element": [element1, ...]}, ...}
    """
    datas = {}
    count = 0
    for root, dirs, files in os.walk(config.json_dir):
        for file in files:
            json_data = parse_json(os.path.join(root, file), config)
            if not json_data:  # 过滤掉不包含有效type和element的rvt文件
                continue
            # 由项目、专业、设计阶段、建筑类型这四个参数确定一个独立的项目
            key = "{}-{}-{}-{}".format(json_data["project"]["Name"],
                                       json_data["project"]["BuildingType"],
                                       json_data["project"]["Major"],
                                       json_data["project"]["Status"])
            if key not in datas:
                count += 1
                if count > num:
                    return datas
                datas[key] = {"project": json_data["project"], "type": [], "element": []}
            # 如果rvt文件从属于同一个项目，则将type_info和element_info合并起来
            datas[key]["type"] += json_data["type"]
            datas[key]["element"] += json_data["element"]
    return datas


@print_run_time
def gen_type_and_proj_datasets(save_dataset=True):
    """
    从原始数据集中获取所有type
    :return: A dict: key -> uniqueId, value -> new uuid，一个由旧的type uniqueId到新的type uuid的映射表
             A dict: key -> new uuid, value -> type info, 新的type uuid与实际type info的映射表
    """
    raw_data = load_raw_data(Config())

    key2new_uuid = {}  # 存储type关键词与新type uuid的映射关系
    unique_id2uuid = {}  # 存储旧type uniqueId与新type uuid的映射关系
    new_uuid2type = {}  # 存储type uuid与实际type info的映射关系
    new_projs = {}
    tmp_dict = {}  # 临时存储命名不规范的type
    for proj_key, proj in raw_data.items():
        for type in proj["type"]:
            # 1.命名不规范的type预处理，形如“类型+数字”的type
            if re.match("墙(\s*)([0-9]*)", type["Name"]) or \
               re.match("外墙(\s*)([0-9]*)", type["Name"]) or \
               re.match("屋顶(\s*)([0-9]*)", type["Name"]) or \
               re.match("柱(\s*)([0-9]*)", type["Name"]) or \
               re.match("结构基础(\s*)([0-9]*)", type["Name"]) or \
               re.match("加密(\s*)([0-9]*)", type["Name"]) or \
               re.match("墙身(\s*)([0-9]*)", type["FamilyName"]) or \
               re.match("常规模型(\s*)([0-9]*)", type["FamilyName"]) or \
               re.match("栏杆(\s*)([0-9]*)", type["FamilyName"]) or \
               re.match("家具(\s*)([0-9]*)", type["FamilyName"]):
                key = "-".join([re.sub("[0-9]", "", type["CategoryName"]).strip(),
                                re.sub("[0-9]", "", type["FamilyName"].strip()),
                                re.sub("[0-9]", "", type["Name"].strip()),
                                type["OtherProperties"]])
                if key in tmp_dict:
                    # 如果规范后的关键词在临时字典种已经存在的话，就直接由字典中的type uniqueId映射到新的type uuid，结束当前循环
                    unique_id2uuid[type["Id"]] = unique_id2uuid[tmp_dict[key]]
                    continue
                else:
                    # 否则将新的key和对应的type存入字典，继续执行下面规范化type的id映射
                    tmp_dict[key] = type["Id"]

            # 2.根据标签判别type
            key = "-".join([type["FamilyType"]] +
                           list(map(str.strip, re.split(r"[_-]", type["CategoryName"]))) +
                           list(map(str.strip, re.split(r"[_-]", type["FamilyName"]))) +
                           list(map(str.strip, re.split(r"[_-]", type["Name"]))))
            # 3.根据uniqueId判别type
            pass

            # 4.为每个唯一的type生成新的uuid作为key
            if key not in key2new_uuid:
                new_uuid = str(uuid.uuid4())  # 为新鉴别出的type生成uuid
                key2new_uuid[key] = new_uuid
                unique_id2uuid[type["Id"]] = new_uuid
                new_uuid2type[new_uuid] = type
            else:
                unique_id2uuid[type["Id"]] = key2new_uuid[key]

        # 5.根据unique_id2uuid映射表更新element的新type id
        new_projs[proj_key] = {"project": proj["project"], "element": []}
        for elem in proj["element"]:
            elem["TypeId"] = unique_id2uuid[elem["TypeId"]]
            new_projs[proj_key]["element"].append(elem)

    # 6.将所有type信息保存到文件构成数据集
    if save_dataset:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "data/valid_types.json"), "w") as f:
            json.dump(new_uuid2type, f)
            print("加载入 valid_types.json 完成...")
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "data/valid_projs.json"), "w") as f:
            json.dump(new_projs, f)
            print("加载入 valid_projs.json 完成...")
    return new_uuid2type, new_projs


@print_run_time
def load_dataset():
    """
    从"/data/valid_projs.txt"、"/data/valid_types.txt"读取预处理好的数据
    :return:
    """
    types = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        "data/valid_types.json"), "r"))
    projs = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        "data/valid_projs.json"), "r"))
    print(len(types))
    return types, projs


def get_original_type(new_uuid: str):
    """
    根据uuid查询原始的type信息
    :param new_uuid:
    :return:
    """
    types = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        "data/valid_types.json"), "r"))
    return types[new_uuid]
