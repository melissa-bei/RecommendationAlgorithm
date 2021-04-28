#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/3/24 11:14
================================================="""
from data_preparation.generate_datasets import gen_type_and_proj_datasets, load_dataset
from data_preparation.preprocessing import get_type_cate2, get_type_frequency, cate2feature


def main():
    # gen_type_and_proj_datasets()
    types, projs = load_dataset()
    types_cates = get_type_cate2(types)
    tag_frequency = get_type_frequency(projs, types_cates)
    m, cates = cate2feature(types_cates)


if __name__ == "__main__":
    main()
