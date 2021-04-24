#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Created on Thu Nov 26 23:12:15 2020
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994
# Reference:  https://github.com/someus/

"""
本模块(textrank.textrank4keywords)用于抽取具体文本中的关键词项。
"""

from segmentation import WordSegmentation
from utils import compute_word_scores

# TODO(zhuoyin94@163.com): 调用sklearn.utils的API对输入类型进行检测，完善异常处理
class TextRank4Keywords():
    """依据PageRank算法与语料，构建图结构并抽取关键词。

    @Parameters:
    ----------
        tokenizer: {object-like}
            WordSegmentation类型的分词器。

    @Attributes:
    ----------
        self.words_no_filter:
            语料分词后，不经任何处理。
        self.words_no_stop_words:
            滤除停用词后的分词后的语料。
        self.words_all_filters:
            依据词性与停用词进行清洗后的分词结果。

    @References:
    ----------
    [1] https://github.com/letiantian/TextRank4ZH
    [2] https://github.com/lancopku/pkuseg-python
    """
    def __init__(self, tokenizer=None):
        self.words_no_filter = None
        self.words_no_stop_words = None
        self.words_all_filters = None

        if tokenizer is None:
            self.tokenizer = WordSegmentation(is_lower=True,
                                              is_use_stop_words=False,
                                              is_use_word_tags_filter=False)
        else:
            self.tokenizer = tokenizer

    def fit_predict(self, text,
                    window_size=2,
                    vertex_source="all_filters",
                    edge_source="no_stop_words",
                    pagerank_config=None):
        """对语料text进行关键词抽取并返回抽取的关键词与其重要程度。

        @Parameters:
        ----------
            text: {str-like}
                需要抽取关键词的语料。
            vertex_source: {str-like}
                使用什么样的词表构建图的结点。
            edge_source: {int-like}
                使用什么样的词表构建图的边。
            pagerank_config: {dict-like}
                PageRank算法的参数字典，细节可参考文献[1][2]，如：
                {'alpha': 0.85}

        @Return:
        ----------
            按词性重要度排序的关键词list，如：
                [['系统', 0.0145], ['列车', 0.0141],
                ['行业', 0.0136], ['智慧', 0.0128],
                ['交通', 0.0127], ['公司', 0.0117],
                ...]
        """
        if not pagerank_config:
            pagerank_config = {"alpha": 0.85}

        # TODO(zhuoyin94@163.com): 此处进行了三次同样类型的分词，可提升效率
        # 不同种类的分词策略
        self.words_no_filter = self.tokenizer.segment_paragraph(text)

        self.words_no_stop_words = self.tokenizer.segment_paragraph(
            text, is_lower=True, is_use_stop_words=True,
            is_use_word_tags_filter=False)
        self.words_no_stop_words = [item for item in self.words_no_stop_words \
                                    if len(item) > 0]

        self.words_all_filters = self.tokenizer.segment_paragraph(
            text, is_lower=True, is_use_stop_words=True,
            is_use_word_tags_filter=False)
        self.words_all_filters = [item for item in self.words_all_filters \
                                  if len(item) > 0]

        if vertex_source == "all_filters":
            vertex_source_tmp = self.words_all_filters
        else:
            vertex_source_tmp = self.words_no_filter

        if edge_source == "no_stop_words":
            edge_source_tmp = self.words_no_stop_words
        else:
            edge_source_tmp = self.words_no_filter

        # 依据PageRank算法，计算每个词的重要程度
        self.keywords = compute_word_scores(vertex_source_tmp,
                                            edge_source_tmp,
                                            window_size=window_size,
                                            pagerank_config=pagerank_config)
        return self.keywords
