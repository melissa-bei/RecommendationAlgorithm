#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/5/13 14:45
================================================="""
import os
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.nlp.v20190408 import nlp_client, models


class TencentNLPCommand:
    def __init__(self):
        self.cred = credential.Credential("AKIDiBoAJMB4cttgCSuIzPec8NL3ZwZxcRXR", "whaCXewykHemdDXoyra5RZQ01mGUBpDK")
        self.httpProfile = HttpProfile()
        self.httpProfile.endpoint = "nlp.tencentcloudapi.com"

        self.clientProfile = ClientProfile()
        self.clientProfile.httpProfile = self.httpProfile
        self.client = nlp_client.NlpClient(self.cred, "ap-guangzhou", self.clientProfile)

    def __getattr__(self, *args, **kwargs):
        return getattr(self.client, *args, **kwargs)


class TextSimilarityCommend(TencentNLPCommand):
    def __init__(self):
        super(TencentNLPCommand, self).__init__()
        self.req = models.TextSimilarityRequest()

    def _set_param(self, src, target):
        params = {"SrcText": src, "TargetText": target}
        self.req.from_json_string(json.dumps(params))

    def get_text_similarity(self, src, target):
        self._set_param(src, target)
        return self.comm.client.TextSimilarity(self.req)


def test_text_similarity():
    type_cates = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                             "data/cb_type_cates.json"), "r", encoding="utf8"))
    type_cates_list = list(sorted(set("-".join(t[0][1:]) for t in type_cates.values())))
    standard_types = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                 "data/standard_vocab.json"), "r", encoding="utf8"))
    standard_types_list = list(sorted(set(["-".join(t["构件类型"] + [t["name"]]) for t in standard_types])))  # 去重

    # 读取之前计算过相似度的数据
    prefix = "sim_result_tencentnlp_tmp_ssssss"  # "sim_result_tencentnlp_"
    record = {}
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")):
        for file in files:
            if file.startswith(prefix) and file.endswith(".txt") and len(file) == len(prefix + "0000.txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf8") as fr:
                    for k in fr.readlines():
                        record.update(json.loads(k))

    # 计算存储起点文件夹
    file_size = 110
    with open("tencentnlp_tmp.txt", "w", encoding="utf-8") as fw:  # 临时存储的文件
        try:
            strings = ""
            result = {}
            comm = TextSimilarityCommend()
            # # 查找上次断点
            # for i in range(len(type_cates_list)):
            #     if type_cates_list[i] not in record:
            #         start_tag = i
            #         break
            # 从断点开始计算相似度
            for i in [88, 301, 195, 226,  81,  77, 291, 149,  # 墙
                      805, 815, 790, 782, 781, 818, 819, 795,  # 窗
                      985, 1038, 961, 947, 995, 1044, 941, 978, 999, 981,  # 门
                      891, 866, 900, 879, 931, 864, 903, 888]:  # 基础 # range(start_tag, len(type_cates_list)):
                batch_size = 100  # 每次送入的目标短语的数量
                start = 0
                print(i+1)

                while start < len(standard_types_list):
                    if start + batch_size <= len(standard_types_list):
                        src, target = type_cates_list[i], standard_types_list[start: start + batch_size]
                    else:
                        src, target = type_cates_list[i], standard_types_list[start:]

                    resp = comm.get_text_similarity(src, target)  # 计算相似度
                    print(resp)

                    if type_cates_list[i] not in result:
                        result[type_cates_list[i]] = []
                    # 整合一个“SrcText”与所有“TargetText”之间的相似度
                    # result[type_cates_list[i]] += [{"Score": 100, "a": "a"}]
                    result[type_cates_list[i]] += [{"Score": resp.Similarity[i].Score, "Text": resp.Similarity[i].Text}
                                                   for i in range(len(resp.Similarity))]
                    start += batch_size

                result[type_cates_list[i]].sort(key=lambda x: x["Score"], reverse=True)  # 排序
                # 临时记录，防止代码因断电、出错、调试暂停等操作丢失数据
                fw.write(json.dumps({type_cates_list[i]: result[type_cates_list[i]]}, ensure_ascii=False) + "\n")
                # 分段保存结果，每个文件中保存file_size大小的“SrcText”的相似度结果，防止一个文件太大不便于打开
                if (i + 1) % file_size == 0:
                    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                           "data/" + prefix + "{0:04d}.txt".format(int((i + 1) / file_size) - 1 + 1)),
                              "a", encoding="utf-8") as fw1:
                        for k in list(result.keys()):
                            strings += json.dumps({k: result[k]}, ensure_ascii=False) + "\n"
                        fw1.write(strings)
                        strings = ""
                        result.clear()
            if strings:
                with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                       "data/" + prefix + "{0:04d}.txt".format(int((i + 1) / file_size) - 1 + 1)),
                          "a", encoding="utf-8") as fw1:
                    for k in list(result.keys()):
                        strings += json.dumps({k: result[k]}, ensure_ascii=False) + "\n"
                    fw1.write(strings)

        except TencentCloudSDKException as err:
            print(err)


if __name__ == "__main__":
    test_text_similarity()
