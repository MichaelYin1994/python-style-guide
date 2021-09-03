#!/usr/local/bin python
# -*- coding: utf-8 -*-

# Created on 202108311136
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994

'''
数据处理与特征工程辅助代码。
'''

import pickle
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import tensorflow as tf
from numba import njit
from tqdm import tqdm

from sklearn.metrics import auc, precision_recall_curve

warnings.filterwarnings('ignore')
###############################################################################
@njit
def adjust_predict_label(true_label, pred_label, delay):
    '''按照delay参数与实际标签，调整预测标签'''
    split_idx = np.arange(0, len(pred_label) - 1) + 1
    split_cond = (true_label[1:] != true_label[:-1])
    split_idx = split_idx[split_cond]

    # 扫描数组，按照要求重组样本标签
    # http://iops.ai/competition_detail/?competition_id=5&flag=1
    front, is_segment_anomaly = 0, true_label[0] == 1
    adjusted_pred_label = pred_label.copy()
    for rear in split_idx:
        if is_segment_anomaly:
            if 1 in pred_label[front:min(front + delay + 1, rear)]:
                adjusted_pred_label[front:rear] = 1
            else:
                adjusted_pred_label[front:rear] = 0

        is_segment_anomaly = not is_segment_anomaly
        front = rear

    if is_segment_anomaly:
        if 1 in pred_label[front:]:
            adjusted_pred_label[front:rear] = 1
        else:
            adjusted_pred_label[front:rear] = 0

    return adjusted_pred_label


@njit
def reconstruct_label(timestamp, label):
    '''依据最小采样间隔，重新组织预测标签'''
    timestamp_sorted_idx = np.argsort(timestamp)
    timestamp_sorted = timestamp[timestamp_sorted_idx]
    label_sorted = label[timestamp_sorted_idx]

    # 获取样本最小采样间隔
    min_interval = np.min(np.diff(timestamp_sorted))

    # 依据最小采样间隔，重构标签与timestamp数组
    new_timestamp = np.arange(
        int(np.min(timestamp)),
        int(np.max(timestamp)) + int(min_interval),
        int(min_interval)
    )
    new_label = np.zeros((len(new_timestamp), ))
    new_label_idx = (timestamp_sorted - timestamp_sorted[0]) // min_interval
    new_label[new_label_idx] = label_sorted

    return label


@njit
def njit_f1(y_true_label, y_pred_label):
    '''计算F1分数，使用njit加速计算'''
    # https://www.itread01.com/content/1544007604.html
    tp = np.sum(np.logical_and(np.equal(y_true_label, 1),
                               np.equal(y_pred_label, 1)))
    fp = np.sum(np.logical_and(np.equal(y_true_label, 0),
                               np.equal(y_pred_label, 1)))
    # tn = np.sum(np.logical_and(np.equal(y_true, 1),
    #                            np.equal(y_pred_label, 0)))
    fn = np.sum(np.logical_and(np.equal(y_true_label, 1),
                               np.equal(y_pred_label, 0)))

    if (tp + fp) == 0:
        precision = 0
    else:
        precision = tp / (tp + fp)

    if (tp + fn) == 0:
        recall = 0
    else:
        recall = tp / (tp + fn)

    if (precision + recall) == 0:
        f1 = 0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return f1, precision, recall


def pr_auc_score(y_true, y_pred):
    '''PR Curve AUC计算方法'''
    precision, recall, _ =  precision_recall_curve(
        y_true.reshape(-1, 1), y_pred.reshape(-1, 1)
    )
    auc_score = auc(recall, precision)

    return auc_score


def evaluate_df_score(true_df, pred_df, delay=7):
    '''依据比赛[1]与论文[2]的评测方法计算KPI预测结果的分数。DataFrame必须
    包括3列："kpi_id", "label"与"timestamp"。其中timestamp列为unix-like时间戳。

    @Parameters:
    ----------
    true_df: {pandas DataFrame}
        标签DataFrame，包含"kpi_id", "label"与"timestamp"三列。
    pred_df: {pandas DataFrame}
        预测结果的DataFrame，包含"kpi_id", "label"与"timestamp"三列。
    delay: {int}
        容错范围，delay \in [0, +\inf]，delay越小评测越严格。

    @Returens:
    ----------
    dict类型，不同kpi_id计算的分数与整体计算的分数。

    @References:
    ----------
    [1] http://iops.ai/competition_detail/?competition_id=5&flag=1
    [2] Zhao, Nengwen, et al. "Label-less: A semi-automatic labelling tool for kpi anomalies." IEEE INFOCOM 2019-IEEE Conference on Computer Communications. IEEE, 2019.

    TODO(zhuoyin94@163.com):
    ----------
    官方评测Metric在未发生故障的segment部分存在不合理设计。更合理
    的Metric应该是按整segment为单位计算F1。
    '''
    if len(true_df) != len(pred_df):
        raise ValueError('Predicting result shape mismatch !')
    for name in ['kpi_id', 'label', 'timestamp']:
        if name not in true_df.columns or name not in pred_df.columns:
            raise ValueError('{} not present in DataFrame !'.format(name))

    # 计算每条KPI曲线的分数
    unique_kpi_ids_list = true_df['kpi_id'].unique().tolist()
    adjusted_pred_label_list, true_label_list = [], []
    f1_score, precision_score, recall_score = [], [], []

    for kpi_id in unique_kpi_ids_list:
        true_df_tmp = true_df[true_df['kpi_id'] == kpi_id]
        pred_df_tmp = pred_df[pred_df['kpi_id'] == kpi_id]

        true_label_tmp = reconstruct_label(
            true_df_tmp['timestamp'].values,
            true_df_tmp['label'].values,
        )
        pred_label_tmp = reconstruct_label(
            pred_df_tmp['timestamp'].values,
            pred_df_tmp['label'].values,
        )
        pred_label_adjusted_tmp = adjust_predict_label(
            true_label_tmp, pred_label_tmp, delay
        )
        f1, precision, recall = njit_f1(
            true_label_tmp, pred_label_adjusted_tmp
        )

        # 保留计算结果
        true_label_list.append(true_label_tmp)
        adjusted_pred_label_list.append(pred_label_adjusted_tmp)

        f1_score.append(f1)
        precision_score.append(precision)
        recall_score.append(recall)

    # 计算整体的分数（体现算法通用性）
    true_label_array = np.concatenate(true_label_list)
    adjusted_pred_label_array = np.concatenate(adjusted_pred_label_list)

    f1_total, precision_total, recall_total = njit_f1(
        true_label_array, adjusted_pred_label_array
    )

    # 保存并返回全部计算结果
    score_dict = {}
    score_dict['f1_score_list'] = f1_score
    score_dict['precision_score_list'] = precision_score
    score_dict['recall_score_list'] = recall_score
    score_dict['total_score'] = [f1_total, precision_total, recall_total]

    return score_dict


class LoadSave():
    '''以*.pkl格式，利用pickle包存储各种形式（*.npz, list etc.）的数据。

    @Attributes:
    ----------
        dir_name: {str-like}
            数据希望读取/存储的路径信息。
        file_name: {str-like}
            希望读取与存储的数据文件名。
        verbose: {int-like}
            是否打印存储路径信息。
    '''
    def __init__(self, dir_name=None, file_name=None, verbose=1):
        if dir_name is None:
            self.dir_name = './data_tmp/'
        else:
            self.dir_name = dir_name
        self.file_name = file_name
        self.verbose = verbose

    def save_data(self, dir_name=None, file_name=None, data_file=None):
        '''将data_file保存到dir_name下以file_name命名。'''
        if data_file is None:
            raise ValueError('LoadSave: Empty data_file !')

        if dir_name is None or not isinstance(dir_name, str):
            dir_name = self.dir_name
        if file_name is None:
            file_name = self.file_name
        if not isinstance(file_name, str) or not file_name.endswith('.pkl'):
            raise ValueError('LoadSave: Invalid file_name !')

        # 保存数据以指定名称到指定路径
        full_name = dir_name + file_name
        with open(full_name, 'wb') as file_obj:
            pickle.dump(data_file, file_obj, protocol=4)

        if self.verbose:
            print('[INFO] {} LoadSave: Save to dir {} with name {}'.format(
                str(datetime.now())[:-4], dir_name, file_name))

    def load_data(self, dir_name=None, file_name=None):
        '''从指定的dir_name载入名字为file_name的文件到内存里。'''
        if dir_name is None or not isinstance(dir_name, str):
            dir_name = self.dir_name
        if file_name is None:
            file_name = self.file_name
        if not isinstance(file_name, str) or not file_name.endswith('.pkl'):
            raise ValueError('LoadSave: Invalid file_name !')

        # 从指定路径导入指定文件名的数据
        full_name = dir_name + file_name
        with open(full_name, 'rb') as file_obj:
            data_loaded = pickle.load(file_obj)

        if self.verbose:
            print('[INFO] {} LoadSave: Load from dir {} with name {}'.format(
                str(datetime.now())[:-4], dir_name, file_name))
        return data_loaded


def basic_feature_report(data_table, quantile=None):
    '''抽取Pandas的DataFrame的基础信息。'''
    if quantile is None:
        quantile = [0.25, 0.5, 0.75, 0.95, 0.99]

    # 基础统计数据
    data_table_report = data_table.isnull().sum()
    data_table_report = pd.DataFrame(data_table_report, columns=['#missing'])

    data_table_report['#uniques'] = data_table.nunique(dropna=False).values
    data_table_report['types'] = data_table.dtypes.values
    data_table_report.reset_index(inplace=True)
    data_table_report.rename(columns={'index': 'feature_name'}, inplace=True)

    # 分位数统计特征
    data_table_description = data_table.describe(quantile).transpose()
    data_table_description.reset_index(inplace=True)
    data_table_description.rename(
        columns={'index': 'feature_name'}, inplace=True)
    data_table_report = pd.merge(
        data_table_report, data_table_description,
        on='feature_name', how='left')

    return data_table_report


class LiteModel:
    '''将模型转换为Tensorflow Lite模型，提升推理速度。目前仅支持Keras模型转换。

    @Attributes:
    ----------
    interpreter: {Tensorflow lite transformed object}
        利用tf.lite.interpreter转换后的Keras模型。

    @References:
    ----------
    [1] https://medium.com/@micwurm/using-tensorflow-lite-to-speed-up-predictions-a3954886eb98
    '''

    @classmethod
    def from_file(cls, model_path):
        '''类方法。用于model_path下的模型，一般为*.h5模型。'''
        return LiteModel(tf.lite.Interpreter(model_path=model_path))

    @classmethod
    def from_keras_model(cls, kmodel):
        '''类方法。用于直接转换keras模型。不用实例化类可直接调用该方法，返回
        被转换为tf.lite形式的Keras模型。

        @Attributes:
        ----------
        kmodel: {tf.keras model}
            待转换的Keras模型。

        @Returens:
        ----------
        经过转换的Keras模型。
        '''
        converter = tf.lite.TFLiteConverter.from_keras_model(kmodel)
        tflite_model = converter.convert()
        return LiteModel(tf.lite.Interpreter(model_content=tflite_model))

    def __init__(self, interpreter):
        '''为经过tf.lite.interpreter转换的模型构建构造输入输出的关键参数。

        TODO(zhuoyin94@163.com):
        ----------
        [1] 可添加关键字，指定converter选择采用INT8量化还是混合精度量化。
        [2] 可添加关键字，指定converter选择量化的方式：低延迟还是高推理速度？
        '''
        self.interpreter = interpreter
        self.interpreter.allocate_tensors()

        input_det = self.interpreter.get_input_details()[0]
        output_det = self.interpreter.get_output_details()[0]
        self.input_index = input_det['index']
        self.output_index = output_det['index']
        self.input_shape = input_det['shape']
        self.output_shape = output_det['shape']
        self.input_dtype = input_det['dtype']
        self.output_dtype = output_det['dtype']

    def predict(self, inp):
        inp = inp.astype(self.input_dtype)
        count = inp.shape[0]
        out = np.zeros((count, self.output_shape[1]), dtype=self.output_dtype)
        for i in range(count):
            self.interpreter.set_tensor(self.input_index, inp[i:i+1])
            self.interpreter.invoke()
            out[i] = self.interpreter.get_tensor(self.output_index)[0]
        return out

    def predict_single(self, inp):
        ''' Like predict(), but only for a single record. The input data can be a Python list. '''
        inp = np.array([inp], dtype=self.input_dtype)
        self.interpreter.set_tensor(self.input_index, inp)
        self.interpreter.invoke()
        out = self.interpreter.get_tensor(self.output_index)
        return out[0]
