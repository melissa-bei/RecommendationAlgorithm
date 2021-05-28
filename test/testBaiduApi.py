#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/5/11 15:19
================================================="""
from aip import AipNlp
import os
import json
import time


class NLPCommand:
    def __init__(self):
        self.app_id = '24147333'
        self.api_key = 'WVXpRGf3Lz41FuBsb9xdxxSW'
        self.secret_key = '7Le0HrA2IE9URGVwDn5l2sIRwhiRvyA4'

        self.client = AipNlp(self.app_id, self.api_key, self.secret_key)


def test_word_emb_sim():
    symbol = "word"
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             r"data/sim_result_baidunlp.txt")
    C = NLPCommand()
    record = {}
    with open(file_path, "r", encoding="utf-8") as fw:
        for l in fw:
            try:
                tmp = eval(l)
                if "error_code" in tmp:
                    continue
                if tmp[symbol + "s"][symbol + "_1"] not in record:
                    record[tmp[symbol + "s"][symbol + "_1"]] = {}
                record[tmp[symbol + "s"][symbol + "_1"]][tmp[symbol + "s"][symbol + "_2"]] = tmp["score"]
                if tmp[symbol + "s"][symbol + "_2"] not in record:
                    record[tmp[symbol + "s"][symbol + "_2"]] = {}
                record[tmp[symbol + "s"][symbol + "_2"]][tmp[symbol + "s"][symbol + "_1"]] = tmp["score"]
            except:
                pass
    result = ""
    with open(file_path, "a+", encoding="utf-8") as fw:
        for w1, w2 in [["A-门嵌板-双扇地弹无框铝门", "防火门"]]:
            if w1 not in record or w2 not in record[w1]:
                sim = C.client.wordSimEmbedding(w1, w2)
                result += str(sim) + "\n"
        fw.write(result)


def test_simnet():
    type_cates = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                             "data/cb_type_cates.json"), "r", encoding="utf8"))
    type_cates_list = list(sorted(set("-".join(t[0][1:]) for t in type_cates.values())))  # 去重
    standard_types = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                 "data/standard_vocab.json"), "r", encoding="utf8"))
    standard_types_list = list(sorted(set(["-".join(t["构件类型"] + [t["name"]]) for t in standard_types])))  # 去重

    symbol = "text"

    prefix = "sim_result_baidunlp_tmp_"  # "sim_result_baidunlp_"
    record = {}
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")):
        for file in files:
            if file.startswith(prefix) and file.endswith(".txt") and len(file) == len(prefix + "0000.txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf8") as fr:
                    for k in fr.readlines():
                        record.update(json.loads(k))

    file_size = 110
    with open("baidunlp_tmp.txt", "w", encoding="utf-8") as fw:
        try:
            strings = ""
            result = {}
            comm = NLPCommand()
            for i in [88, 301, 195, 226, 81, 77, 291, 149,  # 墙
                      805, 815, 790, 782, 781, 818, 819, 795,  # 窗
                      985, 1038, 961, 947, 995, 1044, 941, 978, 999, 981,  # 门
                      891, 866, 900, 879, 931, 864, 903, 888]:  # 基础 # range(start_tag, len(type_cates_list)):
                print(i+1)
                if type_cates_list[i] not in record:
                    result[type_cates_list[i]] = []
                elif len(record[type_cates_list[i]]) != len(standard_types_list):
                    result[type_cates_list[i]] = []
                else:
                    continue

                for j in range(len(standard_types_list)):
                    sim = comm.client.simnet(type_cates_list[i], standard_types_list[j])
                    print(str(j+1) + ": " + str({"Score": sim["score"], "Text": sim[symbol + "s"][symbol + "_2"]}))
                    result[type_cates_list[i]] += [{"Score": sim["score"], "Text": sim[symbol + "s"][symbol + "_2"]}]
                    time.sleep(1)

                result[type_cates_list[i]].sort(key=lambda x: x["Score"], reverse=True)  # 排序
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
            raise ex


if __name__ == "__main__":
    # test_word_emb_sim()
    test_simnet()
