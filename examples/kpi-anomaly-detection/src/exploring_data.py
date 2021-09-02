#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 31 19:19:36 2021

@author: zhuoyin94
"""

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

if __name__ == '__main__':
    # 载入train_df数据
    # ----------------
    file_processor = LoadSave(dir_name='../cached_data/')
    train_df = file_processor.load_data(file_name='train_df.pkl')

    meta_df = train_df.groupby(['kpi_id']).agg(
        {'timestamp': [np.min, np.max],
         'label': [lambda x: 1 - np.sum(x.values) / len(x)]}
    )

    new_col_names = []
    for item in meta_df.columns:
        if item[0] == 'time_id':
            new_col_names.append(item[0])
        else:
            new_col_names.append('{}_{}'.format(item[0], item[1]))
    meta_df.columns = new_col_names

    for col in ['timestamp_amin', 'timestamp_amax']:
        meta_df[col] = pd.to_datetime(meta_df[col], unit='s')
