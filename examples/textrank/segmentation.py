#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Created on Thu Nov 26 19:09:53 2020
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994
# Reference:  https://github.com/someus/

"""
本模块(textrank.segmentation)提供了用于中文分词的WordSegmentation类。
"""

import pkuseg
import unicodedata

SENTENCE_DELIMITERS = ["?", "!", ";", "？", "、", ",", ":",
                       "！", "。", "；", "……", "…", "\n", "\t"]
ALLOW_WORD_TAGS = ["an", "i", "j", "l", "n",
                   "nr", "nrfg", "ns", "nt",
                   "nz", "t", "v", "vd", "vn", "eng"]
# cop = re.compile(u"[^\u4e00-\u9faf^*^a-z^A-Z^0-9]")


class WordSegmentation():
    """分词辅助。依据给定条件，将包含句子的列表切分为词的有序集合。

    @Parameters:
    ----------
        is_lower: {bool-like}
            是否将文本中的英文字符置为小写，默认开启。
        is_use_stop_words: {bool-like}
            是否将待处理文本中的停用词滤除，停用词表由stop_words_vocab确定。
        is_use_word_tags_filter: {bool-like}
            是否根据词性对切分后的词语进行清洗。
        allow_word_tags: {list-like}
            允许的词性列表。
        delimiters: {list-like}
            区分段落中句子的分隔符。
        stop_words_vocab: {list-like}
            用户停用词表，默认为空。
        user_vocab: {list-like}
            用户专业词表，默认为空，若是传值则在切词过程中pkuseg不对这些词进行切分。

    @References:
    ----------
    [1] https://github.com/letiantian/TextRank4ZH
    [2] https://github.com/lancopku/pkuseg-python
    """
    def __init__(self,
                 is_lower=True,
                 is_use_stop_words=False,
                 is_use_word_tags_filter=False,
                 allow_word_tags=None,
                 delimiters=None,
                 user_vocab=None,
                 stop_words_vocab=None):
        # 针对输入stop_words的预处理
        self.stop_words = stop_words_vocab or []
        self.stop_words = [word.strip() for word in self.stop_words]
        self.stop_words = set(self.stop_words)
        self.default_user_vocab = user_vocab

        # 类参数
        self.is_lower = is_lower
        self.is_use_stop_words = is_use_stop_words
        self.is_use_word_tags_filter = is_use_word_tags_filter
        if not allow_word_tags:
            self.default_allow_word_tags = list(set(ALLOW_WORD_TAGS))
        else:
            self.default_allow_word_tags = list(set(allow_word_tags))
        if not delimiters:
            self.default_delimiters = list(set(SENTENCE_DELIMITERS))
        else:
            self.default_delimiters = list(set(delimiters))

        # {句子：切分的句子}
        self.sentence_cutted_dict = {}
        self.sentence_cutted_postag_dict = {}

        # TODO(zhuoyin94@163.com): pkuseg的postag需要internet连接获取词表
        self.seg = pkuseg.pkuseg(user_dict=user_vocab, postag=True)

    def segment_sentence(self, sentence,
                         is_lower=None,
                         is_use_stop_words=None,
                         is_use_word_tags_filter=None):
        """对单个句子(sentence)进行分词，以list类型返回分词后的结果。

        @Parameters:
        ----------
            sentence: {str-like}
                需要被分词的句子（字符串类型）。
            is_lower: {bool-like}
                见全局注释。
            is_use_stop_words: {bool-like}
                见全局注释。
            is_use_word_tags_filter: {bool-like}
                见全局注释。

        @Raises:
        ----------
            TypeError: 输入的不是字符串导致类型错误

        @Returns:
        ----------
            pkuseg分词后的单词列表。如：
            "我是中国公民" --->>  [”我“, "是", "中国", "公民"]
        """
        if not isinstance(sentence, str):
            raise TypeError(("The input sentence type should be str, turns " +
                             "out to be: {}".format(type(sentence))))
        if not is_lower:
            is_lower = self.is_lower
        if not is_use_stop_words:
            is_use_stop_words = self.is_use_stop_words
        if not is_use_word_tags_filter:
            is_use_word_tags_filter = self.is_use_word_tags_filter

        # 调用pkuseg，切分句子
        if sentence in self.sentence_cutted_dict and \
            sentence in self.sentence_cutted_postag_dict:
            word_list = self.sentence_cutted_dict[sentence]
            postag_list = self.sentence_cutted_postag_dict[sentence]
        else:
            sentence_cutted = self.seg.cut(sentence)
            word_list = [item[0] for item in sentence_cutted]
            postag_list = [item[1] for item in sentence_cutted]

            self.sentence_cutted_dict[sentence] = word_list
            self.sentence_cutted_postag_dict[sentence] = postag_list

        # STEP 1: 依据词性滤除不满足词性要求的词汇
        if is_use_word_tags_filter:
            word_list_tmp = []
            for i, word in enumerate(word_list):
                if postag_list[i] in self.default_allow_word_tags:
                    word_list_tmp.append(word)
            word_list = word_list_tmp

        # STEP 2: 滤除文本中的特殊符号
        word_list = [word.strip() for word in word_list]
        word_list = [word for word in word_list if len(word) > 0]

        # STEP 3: 转换英文的大小写
        if is_lower:
            word_list = [word.lower() for word in word_list]

        # STEP 4: 依据要求滤除停用词
        if is_use_stop_words:
            word_list_tmp = []
            for i, word in enumerate(word_list):
                if word not in self.stop_words:
                    word_list_tmp.append(word)
            word_list = word_list_tmp
        return word_list

    def segment_sentence_list(self, sentence_list,
                              is_lower=None,
                              is_use_stop_words=None,
                              is_use_word_tags_filter=None):
        """对包含句子集合的列表内的每一个句子进行切分。

        @Parameters:
        ----------
            sentence_list: {list-like}
                需要被分词的句子集合（list类型）。list的每一个元素为一个未被分词的句子。
            is_lower: {bool-like}
                见全局注释。
            is_use_stop_words: {bool-like}
                见全局注释。
            is_use_word_tags_filter: {bool-like}
                见全局注释。

        @Raises:
        ----------
            TypeError: 方法输入不是句子的列表集合导致类型错误

        @Returns:
        ----------
            分词或者分句之后的结果。代码实现参考了文献[1]。分词结果例如：
            [[”我“, "是", "中国", "公民"],
            ...
            ["北京", "工业", "大学"]]
        """
        if not isinstance(sentence_list, list):
            raise TypeError("Invalid input sentence list !")
        if not is_lower:
            is_lower = self.is_lower
        if not is_use_stop_words:
            is_use_stop_words = self.is_use_stop_words
        if not is_use_word_tags_filter:
            is_use_word_tags_filter = self.is_use_word_tags_filter

        sentence_cutted_list = []
        for sentence in sentence_list:
            sentence_cutted_list.append(
                self.segment_sentence(sentence,
                                      is_lower,
                                      is_use_stop_words,
                                      is_use_word_tags_filter))
        return sentence_cutted_list

    def segment_paragraph(self, paragraph=None,
                          is_lower=None,
                          is_use_stop_words=None,
                          is_use_word_tags_filter=None):
        """对广义的文章（句子段落也被认为是文章）依据分割符，切分为句子的列表。

        @Parameters:
        ----------
            paragraph: {str-like}
                需要被分词的句子集合（list类型）。list的每一个元素为一个未被分词的句子。
            is_lower: {bool-like}
                见全局注释。
            is_use_stop_words: {bool-like}
                见全局注释。
            is_use_word_tags_filter: {bool-like}
                见全局注释。

        @Returns:
        ----------
            切分后的句子列表。
        """
        if not isinstance(paragraph, str):
            raise TypeError("Invalid input paragraph type !")
        if not is_lower:
            is_lower = self.is_lower
        if not is_use_stop_words:
            is_use_stop_words = self.is_use_stop_words
        if not is_use_word_tags_filter:
            is_use_word_tags_filter = self.is_use_word_tags_filter

        # STEP 0: 预处理。尽量将paragraph的符号转换为英文字符，提升切分正确率
        paragraph = unicodedata.normalize("NFKC", paragraph)

        # STEP 1: 依据分隔符，将段落切分为句子列表
        tmp = [paragraph]
        for sep in self.default_delimiters:
            sentence_list = tmp
            tmp = []

            for sentence in sentence_list:
                tmp += sentence.split(sep)
        sentence_list = [s.strip() for s in sentence_list if len(s.strip()) > 0]

        # STEP 2: 对句子列表的每一个句子进行分词
        sentence_list_cutted = self.segment_sentence_list(
            sentence_list, is_lower, is_use_stop_words,
            is_use_word_tags_filter)
        return sentence_list_cutted
