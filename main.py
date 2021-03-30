#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/3/24 11:14
================================================="""
from .data_preparation.preprocessing import load_datas
from common.config import Config


def main():
    resource_dir = "E:/cbim_revit_batch/resource"
    data_json_list = load_datas(Config(resource_dir))


if __name__ == "__main__":
    main()
