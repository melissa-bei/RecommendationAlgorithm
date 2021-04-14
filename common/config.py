#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/3/24 15:30
================================================="""
import os
import pandas as pd


class Config(object):
    def __init__(self):
        """
        资源路径相关配置
        """
        resource_dir = r"E:/cbim_revit_batch/resource"
        try:
            resource_dir = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                             "common/resource_dir.txt")).readline().strip()
        except Exception as ex:
            print(ex)
        if resource_dir == "":
            resource_dir = r"E:/cbim_revit_batch/resource"
        self.resource_dir = resource_dir
        self.xlsx_path = os.path.join(self.resource_dir, "revit模型项目级信息.xlsx")
        self.json_dir = os.path.join(self.resource_dir, "exportedjson")

    def set_resource(self, new_resource_dir):
        """
        设置新的资源路径
        :param new_resource_dir:
        :return:
        """
        self.resource_dir = new_resource_dir

    def update_proj_info(self, original_json):
        """
        根据rvt文件名和路径获取相关附加项目信息
        :param original_json:
        :return:
        """
        file_name, file_path = original_json["project_info"]["FileName"], original_json["project_info"]["FilePath"]
        df = pd.read_excel(self.xlsx_path)

        for r in range(2, df.shape[0]):
            if pd.isnull(df['file_name'].values[r]) | pd.isnull(df['file_path'].values[r]):  # 名字为空过滤
                continue
            if (df['file_name'].values[r].replace("_已分离", "").replace(".rvt", "") == file_name.replace("_已分离", ""))\
               & (df['file_path'].values[r] == file_path.replace("\\\\", "\\").replace("\\ ", " ").replace("\\.", ".")[len(self.json_dir)+1:]):
                project = original_json["project_info"]

                project["Name"] = (project["Name"], df['project_name'][r])[~pd.isnull(df['project_name'][r])]

                project["Number"] = (project["Number"], df['project_number'][r])[~pd.isnull(df['project_number'][r])]
                project["Number"] = (project["Number"], "")[project["Number"] == "项目编号"]

                project["IssueDate"] = (project["IssueDate"], df['project_issue_date'][r])[~pd.isnull(df['project_issue_date'][r])]

                project["Status"] = (project["Status"], df['project_phase'][r])[~pd.isnull(df['project_phase'][r])]
                project["Status"] = (project["Status"], "")[project["Status"] == "项目名称"]

                project["PlaceName"] = (project["PlaceName"], df['project_address'][r])[~pd.isnull(df['project_address'][r])]

                project["Latitude"] = (float(project["Latitude"]), float(df['latitude'][r]))[~pd.isnull(df['latitude'][r])]

                project["Longitude"] = (float(project["Longitude"]), float(df['longitude'][r]))[~pd.isnull(df['longitude'][r])]

                project["BuildingType"] = (project["BuildingType"], df['building_type'][r])[~pd.isnull(df['building_type'][r])]
                project["BuildingType"] = (project["BuildingType"], "")[project["BuildingType"] not in ["公建", "住宅"]]

                project["Major"] = (project["Major"], df['major'][r])[~pd.isnull(df['major'][r])]
                project["Major"] = (project["Major"], "")[~project["Major"].isalpha()]

                original_json["project_info"] = project

                break
        return original_json
