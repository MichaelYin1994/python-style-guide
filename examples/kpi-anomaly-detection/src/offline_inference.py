#!/usr/local/bin python
# -*- coding: utf-8 -*-

# Created on 202109021528
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994

'''
本模块（offline_inference.py）离线load测试数据，构造离线特征，
并对测试数据进行inference和结果评估。
'''

import gc
import warnings
from datetime import datetime
import multiprocessing as mp

import numpy as np
import pandas as pd
from tqdm import tqdm

from utils import LoadSave, evaluate_df_score
from compute_feature_engineering import compute_feature_engineering_single_kpi

# 设定全局随机种子，并且屏蔽warnings
GLOBAL_RANDOM_SEED = 2021
np.random.seed(GLOBAL_RANDOM_SEED)
warnings.filterwarnings('ignore')
###############################################################################

def evaluate_test_lgb(model_name, file_name):
    '''指定测试集上评估lgb模型的效果'''
    # 载入test_df数据
    # ----------------
    file_processor = LoadSave(dir_name='../cached_data/')
    test_df = file_processor.load_data(file_name=file_name)
    trained_models, threshold_list = file_processor.load_data(
        dir_name='../models/',
        file_name=MODEL_FILE_NAME)

    # 按kpi_id拆分训练数据
    # ----------------
    unique_kpi_ids = test_df['kpi_id'].unique()

    test_df_list = []
    for kpi_id in unique_kpi_ids:
        test_df_list.append(
            test_df[test_df['kpi_id'] == kpi_id].reset_index(drop=True)
        )

    del test_df
    gc.collect()

    # 多进程并行特征工程
    # ----------------
    with mp.Pool(processes=mp.cpu_count(), maxtasksperchild=1) as p:
        feats_df_list = list(tqdm(p.imap(
            compute_feature_engineering_single_kpi, test_df_list
        ), total=len(test_df_list)))

    # 获取分模型预测结果
    # ----------------
    test_feats_df = pd.concat(
        feats_df_list, axis=0, ignore_index=True
    )
    test_feats = test_feats_df.drop(['label', 'timestamp'], axis=1).values

    print('\n[INFO] {} Offline testing evaluation...'.format(
        str(datetime.now())[:-4]))
    print('==================================')
    test_pred_proba_list = []
    for fold, (model, threshold) in enumerate(
            zip(trained_models[-1:], threshold_list[-1:])
        ):
        test_pred_proba_list.append(model.predict_proba(
            test_feats, num_iteration=model.best_iteration_
        )[:, 1])

        # 评估效果
        test_pred_df = test_feats_df[['kpi_id', 'label', 'timestamp']].copy()
        test_pred_df['label'] = np.where(test_pred_proba_list[-1] >= threshold, 1, 0)
        test_score_dict = evaluate_df_score(test_feats_df, test_pred_df)

        print('-- {} MEAN f1: {:.4f}, precision: {:.4f}, recall: {:.4f}, TOTAL f1: {:.4f}, precision: {:.4f}, recall: {:.4f}'.format(
            str(datetime.now())[:-4], np.mean(test_score_dict['f1_score_list']),
            np.mean(test_score_dict['precision_score_list']),
            np.mean(test_score_dict['recall_score_list']),
            test_score_dict['total_score'][0],
            test_score_dict['total_score'][1],
            test_score_dict['total_score'][2]
        ))
    print('==================================')


if __name__ == '__main__':
    MODEL_FILE_NAME = '8_lgb_nfolds_5_valprauc_459147_valrocauc_86955.pkl'
    TEST_FILE_NAME = 'test_df.pkl'  # test_df_part_x, test_df_part_y, test_df

    # 载入test_df数据
    # ----------------
    evaluate_test_lgb(MODEL_FILE_NAME, TEST_FILE_NAME)
    