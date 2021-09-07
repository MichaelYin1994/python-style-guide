#!/usr/bin/env python3
#!/usr/local/bin python
# -*- coding: utf-8 -*-

# Created on 202108311525
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994

'''
本模块(compute_feature_engineering.py)针对KPI数据进行特征工程。

@References:
----------
[1] https://www.kaggle.com/lucasmorin/running-algos-fe-for-fast-inference
[2] https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
[3] Rakthanmanon, Thanawin, et al. "Searching and mining trillions of time series subsequences under dynamic time warping." Proceedings of the 18th ACM SIGKDD international conference on Knowledge discovery and data mining. 2012.
'''

import gc
import warnings
from datetime import datetime
import multiprocessing as mp

import numpy as np
import pandas as pd
from numba import njit
from tqdm import tqdm

from utils import LoadSave

# 设定全局随机种子，并且屏蔽warnings
GLOBAL_RANDOM_SEED = 2021
np.random.seed(GLOBAL_RANDOM_SEED)
warnings.filterwarnings('ignore')
###############################################################################
@njit
def njit_sliding_window_mean(timestamp, sensor_vals, window_size):
    '''以one-pass的方式计算array的每一个元素给定window_size内的mean。'''
    if not (len(timestamp) == len(sensor_vals)):
        raise ValueError(
            'Timestamp array size mismatch with the sensor_vals array !'
        )

    # 滚动计算每一时刻给定时间窗口内的统计量
    window_mean_vals = np.zeros((len(timestamp), ), dtype=np.float32)
    window_cum_sum, window_count = 0, 0

    front = 0
    for rear in range(len(timestamp)):
        seconds_gap = timestamp[rear] - timestamp[front]

        window_cum_sum += sensor_vals[rear]
        window_count += 1

        # 若是头尾指针窗口时间差不满足范围，则收缩窗口
        if seconds_gap > window_size:
            while(front <= rear and seconds_gap > window_size):
                window_count -= 1
                window_cum_sum -= sensor_vals[front]

                front += 1
                seconds_gap = timestamp[rear] - timestamp[front]
        window_mean_vals[rear] = window_cum_sum / window_count

    return window_mean_vals


@njit
def njit_sliding_window_std(timestamp, sensor_vals, window_size):
    '''以one-pass的方式计算array的每一个元素给定window_size内的std。'''
    if not (len(timestamp) == len(sensor_vals)):
        raise ValueError(
            'Timestamp array size mismatch with the sensor_vals array !'
        )

    # 滚动计算每一时刻给定时间窗口内的统计量
    window_std_vals = np.zeros((len(timestamp), ), dtype=np.float32)
    window_cum_sum, window_cum_sum_square, window_count = 0, 0, 0

    front = 0
    for rear in range(len(timestamp)):
        seconds_gap = timestamp[rear] - timestamp[front]

        window_cum_sum += sensor_vals[rear]
        window_cum_sum_square += sensor_vals[rear]**2
        window_count += 1

        # 若是头尾指针窗口时间差不满足范围，则收缩窗口
        if seconds_gap > window_size:
            while(front <= rear and seconds_gap > window_size):
                window_count -= 1
                window_cum_sum -= sensor_vals[front]
                window_cum_sum_square -= sensor_vals[front]**2

                front += 1
                seconds_gap = timestamp[rear] - timestamp[front]

        window_std_vals[rear] = window_cum_sum_square / window_count - \
            (window_cum_sum / window_count)**2
        window_std_vals[rear] = np.sqrt(window_std_vals[rear])

    return window_std_vals


def njit_sliding_window_weighted_moving_mean(
        timestamp, sensor_vals, window_size, interval
    ):
    '''以one-pass的方式计算array的每一个元素给定window_size内的WMA。'''
    if not (len(timestamp) == len(sensor_vals)):
        raise ValueError(
            'Timestamp array size mismatch with the sensor_vals array !'
        )

    # 滚动计算每一时刻给定时间窗口内的统计量
    pass


def njit_sliding_window_exponentially_weighted_moving_mean():
    pass



def njit_sliding_window_max():
    '''以stream形式，以one-pass的方式计算array的每一个元素给定window_size内的max。'''
    pass


def njit_sliding_window_min():
    pass



def njit_sliding_window_skew():
    pass


def njit_sliding_window_kurtosis():
    pass


@njit
def njit_time_shift(timestamp, sensor_vals, last_seconds):
    '''以one-pass的方式计算array的每一个元素给定offline_inference内的shift。
    并采用LLVM编译器进行加速。
    '''
    if not (len(timestamp) == len(sensor_vals)):
        raise ValueError(
            'Timestamp array size mismatch with the sensor_vals array !'
        )

    # 滚动计算shift
    shifted_vals = np.zeros((len(timestamp), ), dtype=np.float32)

    front = 0
    for rear in range(len(timestamp)):
        seconds_gap = timestamp[rear] - timestamp[front]

        # 若是头尾指针窗口时间差不满足范围，则收缩窗口
        if seconds_gap > last_seconds:
            while(front < rear and seconds_gap > last_seconds):
                front += 1
                seconds_gap = timestamp[rear] - timestamp[front]
        shifted_vals[rear] = sensor_vals[front]

    return shifted_vals


def compute_feature_engineering_single_kpi(df=None):
    '''计算给定KPI曲线的各类统计特征'''
    df_feats, df_feats_names = [], []

    # 基础元信息记录
    # ----------------
    timestamp_array = df['timestamp'].values
    sensor_array = df['value'].values
    min_interval_minutes = int(np.min(np.diff(timestamp_array))) * 60

    # 滑动窗口统计量
    # ----------------

    # 计算滑窗均值
    # *************
    for window_minutes in [1, 2, 3, 6, 10, 16, 32, 60, 120, 240, 360, 720, 1440]:
        window_seconds = int(window_minutes * 60)

        df_feats.append(
            njit_sliding_window_mean(
                timestamp_array, sensor_array, window_size=window_seconds
            ).reshape(-1, 1)
        )
        df_feats_names.append('window_mean_last_{}'.format(window_minutes))

    for window_minutes in [1440 + 360 * i for i in range(1, 8)]:
        window_seconds = int(window_minutes * 60)

        df_feats.append(
            njit_sliding_window_mean(
                timestamp_array, sensor_array, window_size=window_seconds
            ).reshape(-1, 1)
        )
        df_feats_names.append('window_mean_last_{}'.format(window_minutes))

    # 计算滑窗标准差
    # *************
    for window_minutes in [1, 2, 3, 6, 10, 16, 32, 60, 120, 240, 360, 720, 1440]:
        window_seconds = int(window_minutes * 60)

        df_feats.append(
            njit_sliding_window_std(
                timestamp_array, sensor_array, window_size=window_seconds
            ).reshape(-1, 1)
        )
        df_feats_names.append('window_std_last_{}'.format(window_minutes))

    # 计算滑窗EWMA
    # *************


    # 计算滑窗Min, Max
    # *************


    # 计算滑窗ARIMA/AR
    # *************

    # value shift特征
    # ----------------

    # 短时shift
    # *************
    for shift_minutes in [i * min_interval_minutes for i in range(0, 512, 4)]:
        df_feats.append(
            njit_time_shift(
                timestamp_array, sensor_array, last_seconds=shift_minutes * 60
            ).reshape(-1, 1)
        )
        df_feats_names.append('shift_last_{}'.format(shift_minutes))

    # 特征组装
    # ----------------
    df_feats = np.hstack(df_feats)
    df_feats = pd.DataFrame(df_feats, columns=df_feats_names)

    df_feats['kpi_id'] = df['kpi_id'].values
    df_feats['timestamp'] = df['timestamp'].values

    if 'label' in df.columns:
        df_feats['label'] = df['label'].values

    # 重排特征顺序
    new_col_order = ['kpi_id'] + [item for item in df_feats.columns if item != 'kpi_id']
    df_feats = df_feats[new_col_order]

    return df_feats


if __name__ == '__main__':
    # 载入train_df数据
    # ----------------
    file_processor = LoadSave(dir_name='../cached_data/')
    train_df = file_processor.load_data(file_name='train_df.pkl')

    # 按kpi_id拆分训练数据
    # ----------------
    unique_kpi_ids = train_df['kpi_id'].unique()

    train_df_list = []
    for kpi_id in unique_kpi_ids:
        train_df_list.append(
            train_df[train_df['kpi_id'] == kpi_id].reset_index(drop=True)
        )

    del train_df
    gc.collect()

    # 测试特征工程
    # ----------------
    kpi_id = 0
    feat_df_tmp = compute_feature_engineering_single_kpi(
        train_df_list[kpi_id]
    )

    # 多进程并行特征工程
    # ----------------
    with mp.Pool(processes=mp.cpu_count(), maxtasksperchild=1) as p:
        feats_df_list = list(tqdm(p.imap(
            compute_feature_engineering_single_kpi, train_df_list
        ), total=len(train_df_list)))

    # 存储特征数据
    # ----------------
    file_processor = LoadSave(dir_name='../cached_data/')
    file_processor.save_data(
        file_name='train_feats_list.pkl', data_file=feats_df_list
    )
