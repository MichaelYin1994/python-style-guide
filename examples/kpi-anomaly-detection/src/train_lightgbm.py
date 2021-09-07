#!/usr/local/bin python
# -*- coding: utf-8 -*-

# Created on 202108311928
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994

'''
本模块（train_lightgbm.py）训练lgb分类器。
'''

import gc
import os
from datetime import datetime

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from tqdm import tqdm

from utils import LoadSave, evaluate_df_score, pr_auc_score

GLOBAL_RANDOM_SEED = 2021
###############################################################################

def generator_tscv(df_list, n_folds=2, is_shuffle_train=True):
    '''Generator of the data'''

    n_splits = n_folds + 1
    df_size_list = [len(item) for item in df_list]

    for i in range(n_folds):
        train_idx_list = [
            int(np.floor(item / n_splits * (i + 1))) for item in df_size_list
        ]
        valid_idx_list = [
            int(np.ceil(item / n_splits * (i + 2))) for item in df_size_list
        ]

        df_train_list, df_valid_list = [], []
        for j, df in enumerate(df_list):
            df_train_list.append(
                df.iloc[:train_idx_list[j]]
            )
            df_valid_list.append(
                df.iloc[train_idx_list[j]:valid_idx_list[j]]
            )

        df_train = pd.concat(
            df_train_list, axis=0, ignore_index=True
        )
        df_valid = pd.concat(
            df_valid_list, axis=0, ignore_index=True
        )

        # 通过sampling的方式对DataFrame进行随机shuffle
        if is_shuffle_train:
            df_train = df_train.sample(
                frac=1, random_state=GLOBAL_RANDOM_SEED
            )
            df_train.reset_index(drop=True, inplace=True)

        yield i, df_train, df_valid


def feval_precision_recall_auc(y_true, y_pred):
    '''用于lightgbm早停Metric的P-R Curve AUC计算方法'''
    auc_score = pr_auc_score(
        y_true.reshape(-1, 1), y_pred.reshape(-1, 1)
    )

    return 'pr-auc', round(auc_score, 7), True


if __name__ == '__main__':
    # 载入特征数据
    # ----------------
    N_FOLDS = 5
    N_SEARCH = 150
    EARLY_STOPPING_ROUNDS = 200

    lgb_params = {'boosting_type': 'gbdt',
                  'objective': 'binary',
                  'metric': 'custom',
                  'n_estimators': 10000,
                  'num_leaves': 31,
                  'max_depth': 4,
                  'learning_rate': 0.09,
                  'colsample_bytree': 0.95,
                  'subsample': 0.95,
                  'subsample_freq': 1,
                  'reg_alpha': 0,
                  'reg_lambda': 0.01,
                  'random_state': GLOBAL_RANDOM_SEED,
                  'n_jobs': -1,
                  'verbose': -1}

    # 载入特征数据
    # ----------------
    file_processor = LoadSave(dir_name='../cached_data/')
    train_feats_list = file_processor.load_data(
        file_name='train_feats_list.pkl'
    )

    # STAGE 1: 训练分类器，优化AUC Metric
    # ----------------
    y_val_score_df = np.zeros((N_FOLDS, 6))
    trained_model_list, valid_df_list = [], []

    print('\n[INFO] {} LightGBM training start...'.format(
        str(datetime.now())[:-4]))
    print('==================================')
    print('-- train shape: {}, total folds: {}'.format(
        (np.sum([len(df) for df in train_feats_list]),
         train_feats_list[0].shape[1]),
        N_FOLDS))

    for fold, train_df, val_df in generator_tscv(train_feats_list, N_FOLDS):
        train_feats = train_df.drop(['label', 'timestamp'], axis=1).values
        val_feats = val_df.drop(['label', 'timestamp'], axis=1).values

        train_label = train_df['label'].values
        val_label = val_df['label'].values

        # 训练lightgbm模型
        clf = lgb.LGBMClassifier(**lgb_params)
        clf.fit(
            train_feats, train_label,
            eval_set=[(val_feats, val_label)],
            early_stopping_rounds=EARLY_STOPPING_ROUNDS,
            eval_metric=feval_precision_recall_auc,
            categorical_feature=[0],
            verbose=0
        )
        trained_model_list.append(clf)

        # 对validation数据进行预测
        val_pred_df = val_df[['kpi_id', 'label', 'timestamp']].copy()
        val_pred_df['pred_proba'] = clf.predict_proba(
            val_feats, num_iteration=clf.best_iteration_
        )[:, 1]
        valid_df_list.append(val_pred_df)

        # 评估效果
        y_val_score_df[fold, 0] = fold
        y_val_score_df[fold, 1] = clf.best_iteration_
        y_val_score_df[fold, 2] = pr_auc_score(
            val_pred_df['label'].values.reshape(-1, 1),
            val_pred_df['pred_proba'].values.reshape(-1, 1)
        )
        y_val_score_df[fold, 3] = roc_auc_score(
            val_pred_df['label'].values.reshape(-1, 1),
            val_pred_df['pred_proba'].values.reshape(-1, 1)
        )

        print('-- {} folds {}({}), valid iters: {}, mean pr-auc {:7f}, roc-auc: {:.7f}'.format(
            str(datetime.now())[:-4], fold+1, N_FOLDS,
            int(y_val_score_df[fold, 1]),
            y_val_score_df[fold, 2],
            y_val_score_df[fold, 3]))

    print('-- {} TOTAL valid mean pr-auc: {:.7f}, roc-auc: {:.7f}'.format(
        str(datetime.now())[:-4],
        y_val_score_df[fold, 2],
        np.mean(y_val_score_df[fold, 3])
    ))

    y_val_score_df = pd.DataFrame(
        y_val_score_df,
        columns=['folds', 'best_iter', 'val_pr_auc',
                 'val_roc_auc', 'val_total_f1', 'val_best_threshold']
    )

    print('==================================')
    print('[INFO] {} LightGBM training end...'.format(
        str(datetime.now())[:-4]))

    # STAGE 2: 扫描Validation结果，获取最佳切分阈值
    # ----------------
    decision_threshold_list, best_f1_list = [], []

    for fold in tqdm(range(N_FOLDS)):
        decision_threshold_list_tmp = []
        val_df = valid_df_list[fold]
        val_pred_df = val_df.copy()

        best_f1, best_threshold = 0, 0
        for threshold in np.linspace(0.1, 0.9, N_SEARCH):
            val_pred_df['label'] = np.where(
                val_pred_df['pred_proba'] > threshold, 1, 0
            )
            eval_score = evaluate_df_score(val_df, val_pred_df)

            if eval_score['total_score'][0] > best_f1:
                best_f1 = eval_score['total_score'][0]
                best_threshold = threshold
        print('-- {} folds {}({}), best threshold: {:5f}, best f1: {:.5f}'.format(
            str(datetime.now())[:-4], fold+1, N_FOLDS,
            best_threshold, best_f1))
        decision_threshold_list.append(best_threshold)
        best_f1_list.append(best_f1)

    y_val_score_df['val_total_f1'] = best_f1_list
    y_val_score_df['val_best_threshold'] = decision_threshold_list

    # STAGE 3: 保存训练好的模型/阈值与训练日志
    # ----------------
    sub_file_name = '{}_lgb_nfolds_{}_valprauc_{}_valrocauc_{}'.format(
        len(os.listdir('../logs/')) + 1,
        N_FOLDS,
        str(np.round(y_val_score_df['val_pr_auc'].mean(), 6)).split('.')[1],
        str(np.round(y_val_score_df['val_roc_auc'].mean(), 6)).split('.')[1]
    )

    y_val_score_df.to_csv('../logs/{}.csv'.format(sub_file_name), index=False)
    file_processor = LoadSave(dir_name='../models/')
    file_processor.save_data(
        file_name='{}.pkl'.format(sub_file_name),
        data_file=[trained_model_list, decision_threshold_list])
