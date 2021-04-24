#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Created on Thu Nov 26 16:20:47 2020
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994
# Reference:  https://github.com/someus/

"""
本模块(textrank.utils)提供了用于文本关键词挖掘的一些工具，包括文本距离计算
（LCSS距离，Jaccard距离，编辑距离等），对于给定参数基于PageRank的结点重要度
计算方法。
"""

import numpy as np
import networkx as nx

# 全局化随机种子设定
np.random.seed(2020)

def get_word_pair(word_list, window_size=2):
    """根据word_list的元素内容，依据window_size的大小生成词对。

    依据window_size的大小，生成word_list中词汇的词对，构成PageRank算法中图的结
    点与结点之间边的关系。

    @Parameters:
    ----------
        word_list: {list-like}
            句子分词之后的词列表，列表中的每一个元素即句子中的词。
        window_size: {int-like}
            中心词的window_size范围内的词被认为与中心词具有连接关系。

    @Yields:
    ----------
        返回一个生成器。生成器的每次返回一对词的元组。
    """
    if not word_list:
        raise ValueError("word_list must not be empty !")
    if window_size <= 0 or not isinstance(window_size, int):
        raise ValueError(("window_size must be int and " +
                          "greater than 0, not {}".format(window_size)))
    elif window_size < 2:
        window_size = 2

    # 依据window_size大小，扫描word_list，构成词对
    for i in range(1, window_size+1):
        if i >= len(word_list):
            break
        word_list_tmp = word_list[i:]
        word_pair_zip = zip(word_list, word_list_tmp)
        for word_pair in word_pair_zip:
            yield word_pair


def compute_jaccard_similarity(word_list_x, word_list_y):
    """计算word_list_x与word_list_y之间的jaccard距离。

    @Parameters:
    ----------
        word_list_x: {list-like}
            句子分词之后的词列表，列表中的每一个元素即句子中的词。
        word_list_y: {list-like}
            句子分词之后的词列表，列表中的每一个元素即句子中的词。

    @Returns:
    ----------
        返回两个列表之间的jaccard距离。
    """
    if not word_list_x or not word_list_y:
        return 0

    word_set_x, word_set_y = set(word_list_x), set(word_list_y)
    intersect_words = word_set_x.intersection(word_set_y)
    union_words = word_set_x.union(word_set_y)

    return len(intersect_words) / len(union_words)


def compute_edit_similarity(word_list_x, word_list_y):
    """计算word_list_x与word_list_y之间的编辑距离（Edit Distance）。

    @Parameters:
    ----------
        word_list_x: {list-like}
            句子分词之后的词列表，列表中的每一个元素即句子中的词。
        word_list_y: {list-like}
            句子分词之后的词列表，列表中的每一个元素即句子中的词。

    @Returns:
    ----------
        返回两个列表之间的编辑距离。
    """
    length_x, length_y = len(word_list_x), len(word_list_y)
    denominator = length_x + length_y

    # 初始化全局dp矩阵
    dp = np.zeros((length_x+1, length_y+1))
    dp[:, 0] = np.arange(0, length_x+1)
    dp[0, :] = np.arange(0, length_y+1)

    # 动态规划矩阵计算
    for i in range(1, length_x+1):
        for j in range(1, length_y+1):
            if word_list_x[i-1] == word_list_y[j-1]:
                dp[i, j] = dp[i-1, j-1]
            else:
                dp[i, j] = min(dp[i-1, j] + 1,
                               dp[i, j-1] + 1,
                               dp[i-1, j-1] + 2)
    return 1 - dp[-1, -1] / denominator


def compute_lcss_similarity(word_list_x=None, word_list_y=None,
                            max_pos_diff=3):
    """计算word_list_x与word_list_y之间的归一化的最常公共子序列距离（LCSS Distance）。

    @Parameters:
    ----------
        word_list_x: {list-like} or {array-like}
            句子分词之后的词列表，列表中的每一个元素即句子中的词。
        word_list_y: {list-like} or {array-like}
            句子分词之后的词列表，列表中的每一个元素即句子中的词。
        max_pos_diff: {int-like}
            判定不同句子的两个词属于公共子序的最大允许位置差距的范围。

    @Returns:
    ----------
        返回两个列表之间的LCSS距离。
    """
    length_x, length_y = len(word_list_x), len(word_list_y)
    denominator = min(length_x, length_y)

    # 早停条件
    if length_x == 0 or length_y == 0:
        return 0
    if length_x == 1 and word_list_x[0] in word_list_y:
        return 1 / denominator
    if length_x == 1 and word_list_x[0] not in word_list_y:
        return 0
    if length_y == 1 and word_list_y[0] in word_list_x:
        return 1 / denominator
    if length_y == 1 and word_list_y[0] not in word_list_x:
        return 0

    # 动态规划矩阵计算
    dp = np.zeros((length_x+1, length_y+1))
    for i in range(1, length_x+1):
        for j in range(1, length_y+1):
            pos_diff = int(abs(i - j))

            if (pos_diff <= max_pos_diff) and \
               (word_list_x[i-1] == word_list_y[j-1]):
                dp[i, j] = dp[i-1, j-1] + 1
            else:
                dp[i, j] = max(dp[i-1, j], dp[i, j-1])
    return dp[-1, -1] / denominator


def compute_word_scores(vertex_source, edge_source,
                        window_size=2, pagerank_config=None):
    """依据相关参数，计算vertex_source中，每一个结点的PageRank分数。

    PageRank算法用于无监督的计算一个图中每一个结点的重要程度。当用于关键词提取
    算法时，PageRank算法将句子中的词视作是图的结点；给定窗口内的词与词的共现关系
    作为图的边的构建依据。详细计算方法参见文献[1][2]。

    @Parameters:
    ----------
        vertex_source: {list-like}
            分词后的句子的集合，用于构建图的结点。
        edge_source: {list-like}
            分词之后的句子集合，用于构建图的边关系。
        window_size: {int-like}
            滑窗尺寸的大小。
        pagerank_config: {dict-like}
            PageRank算法的参数字典，细节可参考文献[1][2]，如：
            {'alpha': 0.85}

    @Returns:
    ----------
        返回每个词的PageRank分数。

    @References:
    ----------
    [1] 李航. 统计学习方法. 清华大学出版社, 2012.
    [2] https://networkx.org/documentation/networkx-1.10/reference/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html
    """
    if not vertex_source or not edge_source:
        raise ValueError("vertex_source and edge_source must not be empty !")

    if not pagerank_config:
        pagerank_config = {"alpha": 0.85}
    sorted_words = []
    word2index, index2word = {}, {}

    # 扫描每一个句子的每一个词，构建{词: id}与{id: 词}的索引表
    word_index = 0
    for word_list in vertex_source:
        for word in word_list:
            if word not in word2index:
                word2index[word] = word_index
                index2word[word_index] = word
                word_index += 1

    # 构建邻接矩阵（适用于小数据）
    adjacent_mat = np.zeros((len(word2index), len(word2index)))
    for word_list in edge_source:
        for word_x, word_y in get_word_pair(word_list, window_size):
            if word_x in word2index and word_y in word2index:
                index_x = word2index[word_x]
                index_y = word2index[word_y]

                adjacent_mat[index_x][index_y] = 1
                adjacent_mat[index_y][index_x] = 1

    # 计算构建的邻接矩阵的每一个结点的PageRank分数值
    graph = nx.from_numpy_matrix(adjacent_mat)
    vertex_scores = nx.pagerank(graph, **pagerank_config)
    sorted_scores = sorted(
        vertex_scores.items(), key=lambda item: item[1], reverse=True)

    for index, score in sorted_scores:
        sorted_words.append([index2word[index], score])
    return sorted_words


# TODO(zhuoyin94@163.com): 稀疏PageRank算法
def compute_word_scores_sp(vertex_source, edge_source,
                           window_size=2, pagerank_config=None):
    pass
