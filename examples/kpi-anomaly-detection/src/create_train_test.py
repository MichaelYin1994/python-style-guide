#!/usr/bin/env python3
#!/usr/local/bin python
# -*- coding: utf-8 -*-

# Created on 202108311016
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994

'''
本模块(create_train_test.py)针对原始*.csv的KPI数据进行预处理，切分训练与测试数据。
'''

import os

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

import seaborn as sns
import matplotlib.pyplot as plt

from utils import LoadSave

sns.set(style='ticks', font_scale=1.2, palette='deep', color_codes=True)
colors = ['C' + str(i) for i in range(0, 9+1)]

###############################################################################
def load_csv(dir_name, file_name, nrows=100, **kwargs):
    '''从指定路径dir_name读取名为file_name的*.csv文件，nrows指定读取前nrows行。'''
    if dir_name is None or file_name is None or not file_name.endswith('.csv'):
        raise ValueError('Invalid dir_name or file_name !')

    full_name = os.path.join(dir_name + file_name)
    full_name = dir_name + file_name
    data = pd.read_csv(full_name, nrows=nrows, **kwargs)

    return data


def plot_single_kpi(time_stamp, kpi_vals, label):
    '''可视化单条KPI曲线'''
    fig, ax = plt.subplots(figsize=(16, 4))

    # plot kpi curve
    ax.plot(time_stamp, kpi_vals,
            linestyle='--', color='k',
            linewidth=1.5, label="KPI curve")

    # plot anomalies
    anomalies_timestamp = time_stamp[label == 1]
    anomalies_pts = kpi_vals[label == 1]
    ax.plot(anomalies_timestamp, anomalies_pts,
            linestyle=' ', markersize=2.5,
            color='red', marker='.', label="Anomaly")

    ax.grid(True)
    ax.legend(fontsize=10)
    ax.set_xlim(np.min(time_stamp), np.max(time_stamp))
    ax.set_ylabel('KPI Value', fontsize=10)
    ax.set_xlabel('Unix timestamp', fontsize=10)
    ax.tick_params(axis='both', labelsize=10)
    plt.tight_layout()


if __name__ == '__main__':
    # 全局化参数
    # ----------------
    NROWS = None
    IS_PLOT_KPI = False
    TEST_RATIO = 0.3
    TRAIN_PATH = '../data/kpi competition/'

    # 数据预处理：
    # 1. 按时间切分时序数据为训练与测试部分
    # 2. 拆分测试数据，构建流测试输入
    # ----------------
    train_df = load_csv(
        dir_name=TRAIN_PATH, file_name='phase2_train.csv', nrows=NROWS
    )
    test_df = pd.read_hdf(
        os.path.join(TRAIN_PATH, 'phase2_ground_truth.hdf')
    )
    test_df['KPI ID'] = test_df['KPI ID'].apply(str)

    train_df.rename({'KPI ID': 'kpi_id'}, axis=1, inplace=True)
    test_df.rename({'KPI ID': 'kpi_id'}, axis=1, inplace=True)
    train_unique_kpis = train_df['kpi_id'].unique().tolist()
    test_unique_kpis = test_df['kpi_id'].unique().tolist()

    # 对train_df与test_df中的KPI ID进行编码
    # *************
    encoder = LabelEncoder()
    encoder.fit(train_df['kpi_id'].values)
    train_df['kpi_id'] = encoder.transform(train_df['kpi_id'].values)
    test_df['kpi_id'] = encoder.transform(test_df['kpi_id'].values)

    # 绘制1条KPI曲线及其异常点（kpi_id \in [0, 28]）
    if IS_PLOT_KPI:
        kpi_id = 12
        plt.close('all')

        train_tmp_df = train_df[train_df['kpi_id'] == kpi_id]
        plot_single_kpi(
            train_tmp_df['timestamp'].values,
            train_tmp_df['value'].values,
            train_tmp_df['label'].values
        )

    # TODO(zhuoyin94@163.com): 拆分测试数据，进行流测试
    # 拆分测试数据，做两类拆分：
    # 1. 按时间戳范围与预设比例，拆分testing数据
    # 2. 整体测试数据进行流式拆分
    # *************

    # 测试数据拆分为2部分用作评测
    test_df_list = []
    for kpi_id in test_df['kpi_id'].unique():
        test_df_tmp = test_df.query('kpi_id == {}'.format(kpi_id))
        test_df_tmp.reset_index(drop=True, inplace=True)

        test_df_list.append(test_df_tmp)

    test_idx_list = [
        int(np.floor(TEST_RATIO * len(item))) for item in test_df_list
    ]

    test_df_list_part_x, test_df_list_part_y = [], []
    for i in range(len(test_idx_list)):
        test_df_list_part_x.append(
            test_df_list[i].iloc[:test_idx_list[i]]
        )
        test_df_list_part_y.append(
            test_df_list[i].iloc[test_idx_list[i]:].reset_index(drop=True)
        )

    test_df_part_x = pd.concat(
        test_df_list_part_x, axis=0, ignore_index=True
    )
    test_df_part_y = pd.concat(
        test_df_list_part_y, axis=0, ignore_index=True
    )

    # 以*.pkl保存预处理好的数据
    # ----------------
    file_processor = LoadSave(dir_name='../cached_data/')
    file_processor.save_data(file_name='train_df.pkl', data_file=train_df)
    file_processor.save_data(file_name='test_df.pkl', data_file=test_df)

    file_processor.save_data(
        file_name='test_df_part_x.pkl', data_file=test_df_part_x
    )
    file_processor.save_data(
        file_name='test_df_part_y.pkl', data_file=test_df_part_y
    )
