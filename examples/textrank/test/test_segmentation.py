#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Created on Tue Dec 29 10:06:53 2020
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994

import sys
import unicodedata

import pkuseg
if ".." not in sys.path:
    sys.path.append("..")

from segmentation import WordSegmentation

SENTENCE_LIST = ["根据列车运行速度计算安全行进距离",
                 "数据平台和算法集市通过统一的数据总线和算法能力为上层智能智慧业务提供了全面的PaaS（平台即服务）服务",
                 "交控科技还推出了列车远程瞭望系统的视距延伸装置——轨道星链",
                 "公司总裁助理夏夕盛进行了“智慧单轨运行系统的发展及展望”主题演讲",
                 ""]

PARAGRAPH = "2020年10月21-23日，2020年“北京国际城市轨道交通展览会暨高峰论坛”在北京中国国际展览中心隆重举行。作为城市轨道交通信号系统的领军企业，交控科技股份有限公司（以下简称“交控科技”）携列车远程瞭望系统、天枢系统、智能列车乘客服务系统、无感改造、互联互通的CBTC系统、智慧管理、智慧培训等系统解决方案亮相，完整展示了智慧城轨的未来面貌，吸引大量业内专业人士及观众驻足观看交流。"

SENTENCE_LIST_ANONYMOUS = ["381 598 108 109 400 148 100 113",
                           "556 623 623 421 381 312",
                           "108 108 108 623 108 400",
                           "108 108 108 955, 623"]


def test_segment_sentence_list():
    # 一般性测试方法
    seg_tool = pkuseg.pkuseg(postag=True)
    seg = WordSegmentation(is_lower=False,
                           is_use_stop_words=False,
                           is_use_word_tags_filter=False)

    expected = []
    for sentence in SENTENCE_LIST:
        sentence_cutted = seg_tool.cut(sentence)
        sentence_cutted = [item[0] for item in sentence_cutted]
        expected.append(sentence_cutted)
    assert seg.segment_sentence_list(SENTENCE_LIST) == expected

    # 测试停用词滤除方法
    stop_words_vocab = ["根据", "了", "）", "（"]
    seg = WordSegmentation(is_lower=False,
                           is_use_stop_words=True,
                           is_use_word_tags_filter=False,
                           stop_words_vocab=stop_words_vocab)

    expected = []
    for sentence in SENTENCE_LIST:
        sentence_cutted = seg_tool.cut(sentence)
        sentence_cutted = [item[0] for item in sentence_cutted \
                        if item[0] not in stop_words_vocab]
        expected.append(sentence_cutted)
    assert seg.segment_sentence_list(SENTENCE_LIST) == expected

    # 测试基于词性的滤除方法
    allow_word_tags = ["n", "v"]
    seg = WordSegmentation(is_lower=False,
                           is_use_stop_words=False,
                           is_use_word_tags_filter=True,
                           allow_word_tags=allow_word_tags)

    expected = []
    for sentence in SENTENCE_LIST:
        sentence_cutted = seg_tool.cut(sentence)
        sentence_cutted = [item[0] for item in sentence_cutted \
                        if item[1] in allow_word_tags]
        expected.append(sentence_cutted)
    assert seg.segment_sentence_list(SENTENCE_LIST) == expected

    # 测试大小写是否正常转换
    seg = WordSegmentation(is_lower=True)

    expected = []
    for sentence in SENTENCE_LIST:
        sentence_cutted = seg_tool.cut(sentence)
        sentence_cutted = [item[0].lower() for item in sentence_cutted]
        expected.append(sentence_cutted)
    assert seg.segment_sentence_list(SENTENCE_LIST) == expected


def test_segment_paragraph():
    seg_tool = pkuseg.pkuseg(postag=True)
    seg = WordSegmentation(is_lower=False,
                           is_use_stop_words=False,
                           is_use_word_tags_filter=False)

    delimiters = ["。", ",", "、", "？"]
    expected_sentence_list = []
    for token in delimiters:
        if expected_sentence_list:
            tmp = []
            for raw_sentence_list in expected_sentence_list:
                tmp.extend(raw_sentence_list.split(token))
            expected_sentence_list = tmp
        else:
            expected_sentence_list = unicodedata.normalize(
                "NFKC", PARAGRAPH).split(token)
    expected_sentence_list = [item for item in expected_sentence_list \
                              if len(item) >= 1]

    expected = []
    for sentence in expected_sentence_list:
        sentence_cutted = seg_tool.cut(sentence)
        sentence_cutted = [item[0] for item in sentence_cutted]
        expected.append(sentence_cutted)

    assert seg.segment_paragraph(PARAGRAPH) == expected


if __name__ == "__main__":
    test_segment_sentence_list()
