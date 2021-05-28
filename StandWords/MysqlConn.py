#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/4/22 16:20
================================================="""
import pymysql
import pandas as pd
import os
import json


def get_family_info_from_mysqldb(save_dataset=True):
    # 建立连接
    conn = pymysql.connect(
        host='172.16.201.103',
        port=3306,
        user='root',
        password='1qaz2wsx@CBIM',
        db='resource',
        charset='utf8'
    )

    # 获取游标
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 执行sql语句
    # 获取构件库中所有的族（包含各专业）
    sql = 'select i.id, i.name, i.resource_desc ' \
          'from resource_item i, resource_parameter_value pv ' \
          'where i.parameter_code=pv.code and i.resource_lib_id=54 and i.could_be_shown_in_front=1'
    rows = cursor.execute(sql)
    items = cursor.fetchall()
    # 获取所有族的参数
    sql = 'select ip.resource_item_id , i.name, ip.resource_parameter_id, p.name as parameter, pv.id as param_id, pv.value ' \
          'from resource_item i, resource_item_parameter ip, resource_parameter p, resource_parameter_value pv ' \
          'where i.id=ip.resource_item_id and p.id=ip.resource_parameter_id and ip.resource_parameter_value_id=pv.id ' \
          'and (pv.resource_parameter_id=1 or pv.resource_parameter_id=51 or pv.resource_parameter_id=52 ' \
          'or pv.resource_parameter_id=53 or pv.resource_parameter_id=10004) '
    rows = cursor.execute(sql)
    item_params = cursor.fetchall()
    # 获取结构化参数
    sql = 'select pv.id, pv.code, pv.`value` from resource_parameter_value pv ' \
          'where (pv.resource_parameter_id=1 or pv.resource_parameter_id=51 or pv.resource_parameter_id=52 ' \
          'or pv.resource_parameter_id=53 or pv.resource_parameter_id=10004) ' \
          'order by code'
    rows = cursor.execute(sql)
    params = cursor.fetchall()
    # 关闭游标
    cursor.close()
    # 关闭连接
    conn.cursor()

    items_dict = {}
    for idx in range(len(items)):
        # if items[idx]["id"] not in items_dict:
        try:
            items[idx]["resource_desc"] = pd.read_html(items[idx]["resource_desc"], header=0)[0].to_dict(orient="records")
        except:
            pass
        if items[idx]["name"][0] not in ["A", "S"]:  # 过滤土建专业
            continue
        item_id = items[idx]["id"]
        items[idx].pop("id", None)
        items[idx].pop("resource_desc", None)
        items_dict[item_id] = items[idx]

    tmp1 = {c["code"]: c["id"] for c in params if c["code"]}
    tmp2 = {c["id"]: c["value"] for c in params}
    pid2v = {}
    for c in params:
        if not c["code"]:
            pid2v[c["id"]] = [c["value"]]
        else:
            ks = c["code"].split("_")
            pid2v[c["id"]] = []
            for i in range(len(ks)):
                tmp_k = "_".join(ks[:i + 1])
                if tmp1[tmp_k] in pid2v:
                    pid2v[c["id"]].append(tmp2[tmp1[tmp_k]])

    for idx in range(len(item_params)):
        p = item_params[idx]
        iid = p["resource_item_id"]
        if iid in items_dict:
            if p["parameter"] not in items_dict[iid]:
                items_dict[iid][item_params[idx]["parameter"]] = []
            items_dict[iid][item_params[idx]["parameter"]] += pid2v[p["param_id"]]

    # 保存结果
    if save_dataset:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "data/standard_vocab.json"), "w") as f:
            json.dump(list(items_dict.values()), f)
    if save_dataset:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "data/standard_param.json"), "w") as f:
            json.dump(params, f)

    return items_dict


if __name__ == "__main__":
    get_family_info_from_mysqldb()
