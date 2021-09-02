#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Created on Mon Dec 28 15:00:39 2020
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994

import sys
import random
import pytest
import numpy as np
if ".." not in sys.path:
    sys.path.append("..")

from utils import (get_word_pair,
                   compute_jaccard_similarity,
                   compute_edit_similarity,
                   compute_lcss_similarity,
                   compute_word_scores)

SENTENCE_LIST = ["根据列车运行速度计算安全行进距离",
                 "数据平台和算法集市通过统一的数据总线和算法能力为上层智能智慧业务提供了全面的PaaS（平台即服务）服务",
                 "交控科技还推出了列车远程瞭望系统的视距延伸装置——轨道星链",
                 "公司总裁助理夏夕盛进行了“智慧单轨运行系统的发展及展望”主题演讲"]

PARAGRAPH = "2020年10月21-23日，2020年“北京国际城市轨道交通展览会暨高峰论坛”在北京中国国际展览中心隆重举行。作为城市轨道交通信号系统的领军企业，交控科技股份有限公司（以下简称“交控科技”）携列车远程瞭望系统、天枢系统、智能列车乘客服务系统、无感改造、互联互通的CBTC系统、智慧管理、智慧培训等系统解决方案亮相，完整展示了智慧城轨的未来面貌，吸引大量业内专业人士及观众驻足观看交流。"

SENTENCE_LIST_ANONYMOUS = ["381 598 108 109 400 148 100 113",
                      "556 623 623 421 381 312",
                      "108 108 108 623 108 400",
                      "108 108 108 955, 623"]

def test_edit_similarity():
    # edit相似度正确性测试
    text_x = ["A"]
    text_y = ["A"]
    expected = 1 - 0 / (len(text_x) + len(text_y))
    assert compute_edit_similarity(text_x, text_y) == expected

    text_x = ["A", "A"]
    text_y = ["A"]
    expected = 1 - 1 / (len(text_x) + len(text_y))
    assert compute_edit_similarity(text_x, text_y) == expected

    text_x = ["A", "A", "B"]
    text_y = ["A"]
    expected = 1 - 2 / (len(text_x) + len(text_y))
    assert compute_edit_similarity(text_x, text_y) == expected

    # 内存消耗与计算速度测试
    for _ in range(100):
        text_x = ["A", "B", "C", "D"] * np.random.randint(low=10, high=200)
        text_y = ["A", "B", "C"] * np.random.randint(low=10, high=200)
        compute_edit_similarity(text_x, text_y)


def test_lcss_similarity():
    # LCSS相似度正确性测试
    text_x = ["A", "A", "B", "C", "D"]
    text_y = ["A", "B", "C"]
    expected = 3 / min(len(text_x), len(text_y))
    assert compute_lcss_similarity(text_x, text_y) == expected

    text_x = ["A", "A", "B", "C", "D"]
    text_y = ["A", "B", "C", "D"]
    expected = 4 / min(len(text_x), len(text_y))
    assert compute_lcss_similarity(text_x, text_y) == expected

    text_x = ["A", "A", "B", "C", "D"]
    text_y = ["A"]
    expected = 1 / min(len(text_x), len(text_y))
    assert compute_lcss_similarity(text_x, text_y) == expected

    text_x = ["A", "A", "B", "C", "D"]
    text_y = []
    expected = 0
    assert compute_lcss_similarity(text_x, text_y) == expected

    text_x = ["A", "A", "B", "C", "D"]
    text_y = ["A", "A"]
    expected = 2 / min(len(text_x), len(text_y))
    assert compute_lcss_similarity(text_x, text_y) == expected

    # LCSS相似度最大位置差参数(max_pos_diff)测试
    text_x = ["A", "A", "B", "C", "D"]
    text_y = ["E", "F", "G", "A"]
    expected = 0
    assert compute_lcss_similarity(text_x, text_y, max_pos_diff=1) == expected

    text_x = ["A", "A", "B", "C", "D"]
    text_y = ["E", "F", "G", "A"]
    expected = 1 / min(len(text_x), len(text_y))
    assert compute_lcss_similarity(text_x, text_y, max_pos_diff=2) == expected

    # 内存消耗与计算速度测试
    for _ in range(100):
        text_x = ["A", "B", "C", "D"] * np.random.randint(low=10, high=200)
        text_y = ["A", "B", "C"] * np.random.randint(low=10, high=200)
        compute_lcss_similarity(text_x, text_y)


def test_jaccard_similarity():
    # jaccard相似度正确性测试
    text_x = ["A", "A", "B", "C", "D"]
    text_y = ["A", "B", "F"]
    expected = 2 / 5
    assert compute_jaccard_similarity(text_x, text_y) == expected

    text_x = ["A"]
    text_y = ["A", "B", "C", "D"]
    expected = 1 / 4
    assert compute_jaccard_similarity(text_x, text_y) == expected

    text_x = []
    text_y = ["A", "B", "C", "D"]
    expected = 0
    assert compute_jaccard_similarity(text_x, text_y) == expected


def test_get_word_pair():
    text = ["A", "B", "F", "C"]
    expected = [("A", "B"), ("B", "F"),
                ("F", "C"), ("A", "F"),
                ("B", "C")]
    assert list(get_word_pair(text, window_size=2)) == expected

    text = ["A", "B", "F", "C"]
    expected = [("A", "B"), ("B", "F"),
                ("F", "C"), ("A", "F"),
                ("B", "C"), ("A", "C")]
    assert list(get_word_pair(text, window_size=3)) == expected

    text = ["A", "B"]
    expected = [("A", "B")]
    assert list(get_word_pair(text, window_size=10)) == expected

    text = ["A", "B"]
    expected = [("A", "B")]
    assert list(get_word_pair(text, window_size=1)) == expected

    text = []
    with pytest.raises(ValueError, match="word_list must not be empty !"):
        list(get_word_pair(text, window_size=5))

    text = ["A", "B"]
    with pytest.raises(ValueError):
        list(get_word_pair(text, window_size=1.2))


def test_compute_word_scores():
    with pytest.raises(ValueError):
        compute_word_scores(vertex_source=None,
                            edge_source=None)

    with pytest.raises(ValueError):
        compute_word_scores(vertex_source=[1, 2, 3],
                            edge_source=None)

    text_x = ["A", "B"]
    text_y = ["B", "B", "B", "B", "D", "B"]
    print(compute_word_scores(vertex_source=text_x,
                              edge_source=text_y,
                              window_size=2,
                              pagerank_config={"alpha": 0.8}))

    text_x = [[str(i) for i in range(15)] * 2]
    text_y = []
    for i in range(5):
        text_tmp = [str(i) for i in range(100)] * np.random.randint(low=20, high=100)
        random.shuffle(text_tmp)
        text_y.append(text_tmp)
    print(compute_word_scores(vertex_source=text_x,
                              edge_source=text_y,
                              window_size=2,
                              pagerank_config={"alpha": 0.8}))
