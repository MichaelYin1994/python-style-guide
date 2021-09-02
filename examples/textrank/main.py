#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Created on Thu Nov 26 16:25:41 2020
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994
# Reference:  https://github.com/someus/

"""
本模块(textrank.main)用于抽取给定corpus中的关键词汇。
"""

import os
import numpy as np
import pickle

from segmentation import WordSegmentation
from textrank4keywords import TextRank4Keywords

USER_VOCAB = ["交控科技", "智能列车", "乘客服务",
              "首都智慧地铁", "大数据", "边缘计算",
              "大众创业", "万众创新", "中俄", "郜春海",
              "杜马", "天枢", "状态感知"]

np.random.seed(2020)

def load_pkl(path=".//data//", filename=None):
    """从路径.//cached_data//中载入名字为filename的*.pkl"""
    with open(path+filename, "rb") as file:
        data = pickle.load(file)
    return data


def load_stop_words(path=".//stopwords//"):
    """从路径path中导入停用词表"""
    file_names = ["baidu_stopwords.txt", "cn_stopwords.txt",
                  "hit_stopwords.txt", "scu_stopwords.txt"]

    stop_words = []
    for name in file_names:
        try:
            with open(path+name, "r") as f:
                stop_words.extend(f.readlines())
        except:
            raise FileNotFoundError("File {} not found !".format(name))

    # 滤除重复的停用词
    stop_words = list(set(stop_words))
    return stop_words


def load_corpus(path=".//data//"):
    """从路径path中导入需要抽取关键词的语料"""
    path = ".//data//"
    file_names = [name for name in os.listdir(path) if name.endswith(".txt")]

    corpus = []
    for name in file_names:
        with open(path+name, "r") as f:
            tmp = f.readlines()
            tmp = "".join(tmp)
            corpus.append(tmp)
    return corpus


def main(top_k=30):
    test_corpus = load_corpus()
    user_stop_words = load_stop_words()

    tokenizer = WordSegmentation(stop_words_vocab=user_stop_words,
                                 delimiters=["。", "，"],
                                 user_vocab=USER_VOCAB)
    textrank = TextRank4Keywords(tokenizer=tokenizer)

    key_words = []
    for text in test_corpus:
        key_words.append(textrank.fit_predict(
            text, vertex_source="no_stop_words")[:top_k])

    for item in key_words:
        print("\n-----------------")
        print(item)
        print("-----------------")


if __name__ == "__main__":
    main()
