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
          'where i.parameter_code=pv.code and i.resource_lib_id=54  and pv.resource_parameter_id=10004'
    rows = cursor.execute(sql)
    items = cursor.fetchall()
    # 获取所有族的参数
    sql = 'select ip.resource_item_id , i.name, ip.resource_parameter_id, p.name as parameter, pv.value ' \
          'from resource_item i, resource_item_parameter ip, resource_parameter p, resource_parameter_value pv ' \
          'where i.id=ip.resource_item_id and p.id=ip.resource_parameter_id and ip.resource_parameter_value_id=pv.id'
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
        items_dict[items[idx]["id"]] = items[idx]

    for idx in range(len(params)):
        if params[idx]["resource_item_id"] in items_dict:
            if params[idx]["parameter"] not in items_dict[params[idx]["resource_item_id"]]:
                items_dict[params[idx]["resource_item_id"]][params[idx]["parameter"]] = []
            items_dict[params[idx]["resource_item_id"]][params[idx]["parameter"]].append(params[idx]["value"].strip())

    # # 生成词表
    # vocab = set()
    # for item_id, item in items_dict.items():
    #     item_label_list = [item.get("name", "")] + item.get("专业", []) + item.get("构件类型", [])\
    #                       + item.get("软件版本", []) + item.get("标签", [])
    #     item_label_set = set(item_label_list)
    #     vocab.update(item_label_set)

    # sql = 'select i.id, i.name, i.parameter_code, i.resource_desc, i.collected, i.clicked, i.commented, i.download, pv.`value`, ip.resource_parameter_value ' \
    #       'from resource_item i, resource_parameter_value pv, resource_item_parameter ip ' \
    #       'where i.parameter_code=pv.code and i.is_deleted=0 and ip.resource_item_id=i.id and pv.resource_parameter_id=10004' \
    #       'and ip.resource_parameter_id=51 and ip.resource_parameter_value_id=205'
    # 保存结果
    if save_dataset:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "data/standard_vocab.txt"), "w", encoding="utf8") as f:
            f.write("\n".join([str(item) for item in list(items_dict.values())]))
    return items_dict


if __name__ == "__main__":
    get_family_info_from_mysqldb()
