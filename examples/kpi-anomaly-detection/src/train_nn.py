#!/usr/local/bin python
# -*- coding: utf-8 -*-

# Created on 202109061845
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994

'''
本模块（train_nn.py）训练nn分类器。
'''

import gc
import os
from datetime import datetime

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

from utils import LoadSave, evaluate_df_score, pr_auc_score, LiteModel

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


def build_model(verbose=False, is_compile=True, **kwargs):
    '''Building and compiling a simple tabulr neural network with
    residual connection.

    @Parameters:
    ----------
    verbose: {bool-like}
        Whether the model print its structure information or not.
    is_complie: {bool-like}
        Whether we return a compiled model or not.
    **kwargs:
        Other importance parameters。

    @Return:
    ----------
    A keras model.
    '''

    # Important parameters and input layers
    # -------------------
    n_feats = kwargs.pop('n_feats', 128)
    n_tokens = kwargs.pop('n_feats', 128)
    learning_rate = kwargs.pop('lr', 0.001)
    label_smoothing = kwargs.pop('label_smoothing', 0)

    layer_token_input = tf.keras.layers.Input(
        shape=(1, ), name='layer_token_input', dtype='int32'
    )
    layer_dense_input = tf.keras.layers.Input(
        shape=(n_feats, ), name='layer_dense_input', dtype='float32'
    )

    layer_token_embedding = tf.keras.layers.Embedding(
        input_dim=n_tokens, output_dim=32, input_length=1,
    )(layer_token_input)
    layer_token_embedding = tf.keras.layers.Flatten()(layer_token_embedding)

    layer_concat_feats = tf.keras.layers.concatenate(
        [layer_dense_input, layer_token_embedding]
    )

    # Bottleneck network structure
    # -------------------
    layer_dense_init = tf.keras.layers.Dense(
        units=128, activation='relu'
    )(layer_concat_feats)

    x = tf.keras.layers.BatchNormalization()(layer_dense_init)
    x = tf.keras.layers.Dropout(0.4)(x)

    x = tf.keras.layers.Dense(
        units=64, activation='relu'
    )(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.4)(x)

    x = tf.keras.layers.Dense(
        units=64, activation='relu'
    )(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.4)(x)

    x = tf.keras.layers.Dense(
        units=128, activation='relu'
    )(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.4)(x)

    # Local residual connection
    # -------------------
    layer_total_feats = tf.keras.layers.concatenate(
        [layer_dense_init, x]
    )
    layer_total_feats = tf.keras.layers.Dense(
        units=64, activation='relu'
    )(layer_total_feats)
    layer_total_feats = tf.keras.layers.BatchNormalization()(layer_total_feats)
    layer_total_feats = tf.keras.layers.Dropout(0.4)(layer_total_feats)

    layer_pred = tf.keras.layers.Dense(
        1, activation='sigmoid', name='layer_output'
    )(layer_total_feats)

    model = tf.keras.Model(
        [layer_token_input, layer_dense_input], layer_pred
    )

    if verbose:
        model.summary()
    if is_compile:
        model.compile(
            loss='binary_crossentropy',
            optimizer=tf.keras.optimizers.Adam(learning_rate),
            metrics=[
                tf.keras.metrics.AUC(
                    num_thresholds=2000, curve='PR', name='auc'
            )]
        )
    return model


if __name__ == '__main__':
    # 载入特征数据
    # ----------------
    N_FOLDS = 5
    N_EPOCHS = 800
    N_SEARCH = 150
    VERBOSE = 0
    BATCH_SIZE = 32767
    MODEL_LR = 0.0008
    MODEL_LR_DECAY_RATE = 0.6
    DECAY_LR_PATIENCE_ROUNDS = 10
    EARLY_STOP_ROUNDS = 60

    # 载入特征数据
    # ----------------
    file_processor = LoadSave(dir_name='../cached_data/')
    train_feats_list = file_processor.load_data(
        file_name='train_feats_list.pkl'
    )

    # STAGE 1: 训练分类器，优化AUC Metric
    # ----------------
    y_val_score_df = np.zeros((N_FOLDS, 6))
    trained_model_list, trained_normalizer_list = [], []
    valid_df_list = []

    print('\n[INFO] {} NeuralNetwork training start...'.format(
        str(datetime.now())[:-4]))
    print('==================================')
    print('-- train shape: {}, total folds: {}'.format(
        (np.sum([len(df) for df in train_feats_list]),
         train_feats_list[0].shape[1]),
        N_FOLDS))

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_auc', mode='max',
            verbose=1, patience=EARLY_STOP_ROUNDS,
            restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_auc',
                factor=MODEL_LR_DECAY_RATE,
                mode='max',
                patience=DECAY_LR_PATIENCE_ROUNDS,
                min_lr=0.000008),
    ]

    for fold, train_df, val_df in generator_tscv(train_feats_list, N_FOLDS):
        # Padding NaN
        # -----------
        train_df.fillna(0, inplace=True)
        val_df.fillna(0, inplace=True)

        train_feats = train_df.drop(['label', 'timestamp'], axis=1).values
        val_feats = val_df.drop(['label', 'timestamp'], axis=1).values

        train_label = train_df['label'].values
        val_label = val_df['label'].values

        train_token_feats = train_feats[:, 0].reshape(-1, 1)
        train_dense_feats = train_feats[:, 1:]

        val_token_feats = val_feats[:, 0].reshape(-1, 1)
        val_dense_feats = val_feats[:, 1:]

        # STEP 1: 归一化训练与验证数据
        # -----------
        normalizer = StandardScaler()
        normalizer.fit(train_dense_feats)
        train_dense_feats = normalizer.transform(train_dense_feats)
        val_dense_feats = normalizer.transform(val_dense_feats)

        trained_normalizer_list.append(normalizer)

        # STEP 2: 编译并训练神经网络
        # -----------
        nn_model = build_model(
            n_feats=train_dense_feats.shape[1],
            n_tokens=len(np.unique(train_token_feats)),
            lr=MODEL_LR
        )

        nn_model.fit(
            x=[train_token_feats, train_dense_feats], y=train_label,
            validation_data=([val_token_feats, val_dense_feats], val_label),
            epochs=N_EPOCHS,
            batch_size=BATCH_SIZE,
            callbacks=callbacks,
            verbose=VERBOSE
        )
        trained_model_list.append(nn_model)

        # 对validation数据进行预测
        val_pred_df = val_df[['kpi_id', 'label', 'timestamp']].copy()
        val_pred_df['pred_proba'] = nn_model.predict(
            [val_token_feats, val_dense_feats]
        )
        valid_df_list.append(val_pred_df)

        # 评估效果
        y_val_score_df[fold, 0] = fold
        y_val_score_df[fold, 1] = 20
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
    sub_file_name = '{}_nn_nfolds_{}_valprauc_{}_valrocauc_{}'.format(
        len(os.listdir('../logs/')) + 1,
        N_FOLDS,
        str(np.round(y_val_score_df['val_pr_auc'].mean(), 6)).split('.')[1],
        str(np.round(y_val_score_df['val_roc_auc'].mean(), 6)).split('.')[1]
    )
    y_val_score_df.to_csv('../logs/{}.csv'.format(sub_file_name), index=False)

    # 保存模型文件与归一化器
    if 'nn_models' not in os.listdir('../models/'):
        os.mkdir('../models/{}'.format('nn_models'))

    dir_name = '../models/nn_models/'
    file_processor = LoadSave(dir_name=dir_name)
    for fold, model in enumerate(trained_model_list):
        # Save model
        file_name = '{}fold_{}_nn_model'.format(dir_name, fold)
        trained_model_list[fold].save(file_name)

        # Save normalizer and threshold
        file_processor.save_data(
            file_name='fold_{}_nn_model_attachments.pkl'.format(fold),
            data_file=[trained_normalizer_list[fold], decision_threshold_list[fold]]
        )
