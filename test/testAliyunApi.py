#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/5/26 14:15
================================================="""
import json
import os
import time
from aliyunsdkalinlp.request.v20200629 import GetWeChGeneralRequest, GetTsChEcomRequest
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ServerException


class AliNLPCommand:
    def __init__(self):
        self.access_key_id = 'LTAI5tEoh2nV4Wertx8LbdKA'
        self.access_key_secret = 'HBep9Exl9Fd6vnFDx7u54dPyT1vL62'
        self.region_id = 'cn-hangzhou'

        self.client = AcsClient(self.access_key_id, self.access_key_secret, self.region_id)


class WordEmbCommend(AliNLPCommand):
    def __init__(self):
        super().__init__()
        self.req = GetWeChGeneralRequest.GetWeChGeneralRequest()
        self.req.set_ServiceCode("alinlp")

    def _set_param(self, text):
        self.req.set_Text(text)

    def get_word_emd(self, text):
        self._set_param(text)
        resp = self.client.do_action_with_exception(self.req)
        return json.loads(json.loads(resp)["Data"])


class TextSimilarityCommend(AliNLPCommand):
    def __init__(self):
        super().__init__()
        self.req = GetTsChEcomRequest.GetTsChEcomRequest()
        self.req.set_ServiceCode("alinlp")
        self.req.set_Type("similarity")

    def _set_param(self, t, q):
        self.req.set_OriginT(t)
        self.req.set_OriginQ(q)

    def get_text_similarity(self, t, q):
        self._set_param(t, q)
        resp = self.client.do_action_with_exception(self.req)
        return json.loads(json.loads(resp)["Data"])


def test_word_emb():
    try:
        comm = WordEmbCommend()
        resp = comm.get_word_emd("我来自北京")
        print(resp)

    except ServerException as err:
        print(err)


def test_text_similarity():
    type_cates = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                             "data/cb_type_cates.json"), "r", encoding="utf8"))
    type_cates_list = list(sorted(set("-".join(t[0][1:]) for t in type_cates.values())))
    standard_types = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                 "data/standard_vocab.json"), "r", encoding="utf8"))
    standard_types_list = ["-".join(t["构件类型"] + [t["name"]]) for t in standard_types]
    standard_types_list = list(sorted(set(["-".join(t["构件类型"] + [t["name"]]) for t in standard_types])))  # 去重

    # 读取之前计算过相似度的数据
    prefix = "sim_result_alinlp_tmp_"  # "sim_result_alinlp_"
    record = {}
    for root, dirs, files in os.walk(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")):
        for file in files:
            if file.startswith(prefix) and file.endswith(".txt") and len(file) == len(prefix + "0000.txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf8") as fr:
                    for k in fr.readlines():
                        record.update(json.loads(k))

    file_size = 110
    with open("alinlp_tmp.txt", "w", encoding="utf-8") as fw:
        try:
            strings = ""
            result = {}
            comm = TextSimilarityCommend()
            for i in [88, 301, 195, 226, 81, 77, 291, 149,  # 墙
                      805, 815, 790, 782, 781, 818, 819, 795,  # 窗
                      985, 1038, 961, 947, 995, 1044, 941, 978, 999, 981,  # 门
                      891, 866, 900, 879, 931, 864, 903, 888]:  # 基础 # range(start_tag, len(type_cates_list)):
                if type_cates_list[i] in record:
                    continue
                print(i + 1)
                result[type_cates_list[i]] = []
                for j in range(len(standard_types_list)):
                    sim = comm.get_text_similarity(type_cates_list[i], standard_types_list[j])
                    if sim["success"]:
                        print(str(j + 1) + ": " + str({"Score": sim["result"][0]["score"], "Text": standard_types_list[j]}))
                    result[type_cates_list[i]] += [{"Score": sim["result"][0]["score"], "Text": standard_types_list[j]}]
                    time.sleep(0.5)

                result[type_cates_list[i]].sort(key=lambda x: float(x["Score"]), reverse=True)  # 排序
                # 临时记录
                fw.write(json.dumps({type_cates_list[i]: result[type_cates_list[i]]}, ensure_ascii=False) + "\n")
                # 分段保存结果
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

        except Exception as ex:
            print(ex)


if __name__ == "__main__":
    # test_word_emb()
    test_text_similarity()
