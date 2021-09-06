#!/usr/bin/env python3
#!/usr/local/bin python
# -*- coding: utf-8 -*-

# Created on 202109061216
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994

'''
本模块(test_stream_processing.py)用于测试流特征工程的正确性。
'''

import warnings
import pandas as pd
from tqdm import tqdm
import numpy as np
import numba
from numba import njit
from numba.experimental import jitclass

# 设定全局随机种子，并且屏蔽warnings
GLOBAL_RANDOM_SEED = 2021
np.random.seed(GLOBAL_RANDOM_SEED)
warnings.filterwarnings('ignore')

###############################################################################
def generate_simulation_data(n_points=10000, min_interval=20):
    '''生成kpi仿真数据'''
    sensor_vals = np.random.random(n_points)
    timestamp = np.array(
        [i * min_interval for i in range(4 * n_points)], dtype=np.int64
    )

    # 生成随机的时间戳
    rand_idx = np.arange(0, len(timestamp))
    np.random.shuffle(rand_idx)

    timestamp = timestamp[rand_idx[:n_points]]
    timestamp = np.sort(timestamp)

    # 组装数据为pandas DataFrame
    kpi_df = pd.DataFrame(
        {'timestamp': timestamp, 'value': sensor_vals,
         'kpi_id': np.ones((len(timestamp), ))}
    )

    return kpi_df


@njit
def njit_sliding_window_mean(timestamp, sensor_vals, window_size):
    '''以one-pass的方式计算array的每一个元素给定window_size内的mean。
    并采用LLVM编译器进行加速。
    '''
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
        # window_mean_vals[rear] = window_cum_sum / window_count
        window_mean_vals[rear] = np.mean(sensor_vals[front:(rear+1)])

    return window_mean_vals


@njit
def njit_sliding_window_std(timestamp, sensor_vals, window_size):
    '''以one-pass的方式计算array的每一个元素给定window_size内的std。
    并采用LLVM编译器进行加速。
    '''
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

        # window_std_vals[rear] = window_cum_sum_square / window_count - \
        #     (window_cum_sum / window_count)**2
        window_std_vals[rear] = np.std(sensor_vals[front:(rear+1)])

    return window_std_vals


ArrayDeque_kv_ty = (numba.types.unicode_type, numba.types.float64[:])
ArrayDeque_spec = [
    ('interval', numba.int32),
    ('max_time_span', numba.int32),
    ('deque_timestamp', numba.int64[:]),
    ('deque_vals', numba.float64[:]),
    ('deque_size', numba.int32),
    ('deque_front', numba.int32),
    ('deque_rear', numba.int32),
    ('deque_stats', numba.types.DictType(*ArrayDeque_kv_ty))
]
@jitclass(ArrayDeque_spec)
class ArrayDeque():
    '''对于时序流数据（stream data）的高效存储实现。

    采用numpy array模拟deque，deque保存指定时间区间范围内的时序值。每当时间
    范围不满足条件的时候，通过指针移动模拟队尾元素出队；当array满的时候，
    通过重新分配array内存的方法，重组array内容。

    我们实现的ArrayDeque在设计时便考虑了数据流时间戳不均匀的问题，通过移动指针
    的方式高效的实现元素的入队和出队。

    @Attributes:
    ----------
    interval: {int-like}
        元素与元素之间最小的时间间隔单位，默认为秒。
    max_time_span: {int-like}
        deque首元素与尾元素最大允许时间差，默认单位为秒。
    deque_timestamp: {array-like}
        用于存储unix时间戳的数组，模拟双端队列。
    deque_vals: {array-like}
        用于存储实际传感器读数的数组，模拟双端队列。
    deque_size: {int-like}
        deque的大小。
    deque_front: {int-like}
        用于模拟deque范围的deque的头指针。
    deque_rear: {int-like}
        用于模拟deque范围的deque的尾指针，永远指向deque最后一个有值元素索引的下一个元素索引。
    deque_stats: {dict-like}
        deque内部不同时间范围的基础统计量。

    @References:
    ----------
    [1] https://www.kaggle.com/lucasmorin/running-algos-fe-for-fast-inference
    '''
    def __init__(self, interval=20, max_time_span=3600):
        self.interval = interval
        self.max_time_span = max_time_span
        self.deque_size = int(max_time_span // interval * 2) + 1
        self.deque_stats = numba.typed.Dict.empty(
            *ArrayDeque_kv_ty
        )

        self.deque_timestamp = np.zeros((self.deque_size, ), dtype=np.int64)
        self.deque_vals = np.zeros((self.deque_size, ), dtype=np.float64)
        self.deque_front, self.deque_rear = 0, 0

    def push(self, timestep, x):
        '''将一组元素入队'''
        # (timestamp, x) 入队
        self.deque_timestamp[self.deque_rear] = timestep
        self.deque_vals[self.deque_rear] = x

        # 不满足deque时间窗需求，收缩deque范围
        front, rear = self.deque_front, self.deque_rear

        time_gap = self.deque_timestamp[rear] - self.deque_timestamp[front]
        if time_gap > self.max_time_span:
            while(front <= rear and time_gap > self.max_time_span):
                front += 1
                time_gap = self.deque_timestamp[rear] - self.deque_timestamp[front]

        self.deque_front = front
        self.deque_rear += 1

    def update(self):
        '''若队满，则重新调整队列数组内存空间'''
        if self.is_full():
            rear = len(self.deque_timestamp[self.deque_front:])

            self.deque_timestamp = self.adjust_deque_size(
                self.deque_timestamp[self.deque_front:], self.deque_size
            )
            self.deque_vals = self.adjust_deque_size(
                self.deque_vals[self.deque_front:], self.deque_size
            )
            self.deque_front, self.deque_rear = 0, rear

    def adjust_deque_size(self, deque, target_deque_size):
        '''调整deque数组的尺寸到target_deque_size'''
        new_deque = np.zeros((target_deque_size, ))
        new_deque[:len(deque)] = deque
        return new_deque

    def is_full(self):
        '''判断deque是否空间满'''
        return self.deque_rear >= self.deque_size

    def get_window_mean(self, window_size=120):
        '''按stream的方式，抽取mean统计量'''
        if window_size > self.max_time_span or window_size < self.interval:
            raise ValueError('Invalid input window size !')

        # 载入stream参数
        window_size = int(window_size)
        field_name = 'mean_{}'.format(window_size)

        if field_name in self.deque_stats:
            dist2end, window_sum = self.deque_stats[field_name]
        else:
            window_sum = np.nan
            dist2end = self.deque_rear - self.deque_front - 1

        start = int(self.deque_rear - dist2end - 1)
        end = int(self.deque_rear - 1)

        # 重新计算参数
        dist2end, window_sum, mean_res = self.compute_window_mean(
            self.deque_timestamp,
            self.deque_vals,
            start, end, window_sum, window_size
        )

        # 更新预置参数
        new_params = np.array([dist2end, window_sum], dtype=np.float64)
        self.deque_stats[field_name] = new_params

        return mean_res

    def get_window_std(self, window_size=120):
        '''按stream的方式，抽取std统计量'''
        if window_size > self.max_time_span or window_size < self.interval:
            raise ValueError('Invalid input window size !')

        # 载入stream参数
        window_size = int(window_size)
        field_name = 'std_{}'.format(window_size)

        if field_name in self.deque_stats:
            dist2end, window_sum, window_squre_sum = self.deque_stats[field_name]
        else:
            window_sum = np.nan
            window_squre_sum = np.nan
            dist2end = self.deque_rear - self.deque_front - 1

        if field_name in self.deque_stats:
            dist2end, window_sum, window_squre_sum = self.deque_stats[field_name]
        else:
            window_sum = np.nan
            window_squre_sum = np.nan
            dist2end = self.deque_rear - self.deque_front - 1

        start = int(self.deque_rear - dist2end - 1)
        end = int(self.deque_rear - 1)

        # 重新计算参数
        dist2end, window_sum, window_squre_sum, mean_res = self.compute_window_std(
            self.deque_timestamp,
            self.deque_vals,
            start, end, window_sum, window_squre_sum, window_size
        )

        # 更新预置参数
        new_params = np.array([dist2end, window_sum, window_squre_sum], dtype=np.float64)
        self.deque_stats[field_name] = new_params

        return mean_res

    def get_window_shift(self):
        pass

    def get_window_median(self):
        pass

    def get_window_max(self):
        pass

    def get_window_hog_1d(self):
        pass

    def compute_window_std(self, timestamp, sensor_vals,
                           start, end,
                           window_sum, window_squre_sum,
                           max_time_span):
        if np.isnan(window_sum):
            window_sum = np.sum(sensor_vals[start:(end + 1)])
            window_squre_sum = np.sum(sensor_vals[start:(end + 1)]**2)
        else:
            window_sum += sensor_vals[end]
            window_squre_sum += sensor_vals[end]**2

        # STEP 1: 时间窗口放缩，统计量修正
        window_sum_delta = 0
        window_squre_sum_delta = 0
        time_gap = timestamp[end] - timestamp[start]

        if time_gap > max_time_span:
            while(start <= end and time_gap > max_time_span):
                window_sum_delta -= sensor_vals[start]
                window_squre_sum_delta -= sensor_vals[start]**2
                start += 1
                time_gap = timestamp[end] - timestamp[start]

        # STEP 2: 统计量更新
        dist2end = end - start + 1
        window_sum = window_sum + window_sum_delta
        window_squre_sum = window_squre_sum + window_squre_sum_delta
        std_res = window_squre_sum / dist2end - (window_sum / dist2end)**2
        std_res = np.sqrt(std_res)

        return dist2end, window_sum, window_squre_sum, std_res

    def compute_window_mean(self, timestamp, sensor_vals,
                            start, end, window_sum, max_time_span):
        '''依据参数，计算满足窗口尺寸的mean统计量'''
        if np.isnan(window_sum):
            window_sum = np.sum(sensor_vals[start:(end + 1)])
        else:
            window_sum += sensor_vals[end]

        # STEP 1: 时间窗口放缩，统计量修正
        window_sum_delta = 0
        time_gap = timestamp[end] - timestamp[start]

        if time_gap > max_time_span:
            while(start <= end and time_gap > max_time_span):
                window_sum_delta -= sensor_vals[start]
                start += 1
                time_gap = timestamp[end] - timestamp[start]

        # STEP 2: 统计量更新
        dist2end = end - start + 1
        window_sum = window_sum + window_sum_delta
        mean_res = window_sum / dist2end

        return dist2end, window_sum, mean_res



if __name__ == '__main__':
    # 生成kpi仿真数据（单条kpi曲线）
    # *******************
    N_POINTS = 300000
    MIN_INTERVAL = 20
    MAX_TIME_SPAN = int(5 * 24 * 3600)
    WINDOW_SIZE = int(6 * 3600)
    df = generate_simulation_data(n_points=N_POINTS, min_interval=MIN_INTERVAL)

    # 流式抽取统计特征
    # *******************
    stream_deque = ArrayDeque(
        interval=MIN_INTERVAL, max_time_span=MAX_TIME_SPAN
    )

    window_mean_results = []
    window_std_results = []
    for timestep, sensor_val in tqdm(df[['timestamp', 'value']].values):
        # 元素入队
        stream_deque.push(timestep, sensor_val)

        # # 统计量计算
        # window_mean_results.append(
        #     stream_deque.get_window_mean(window_size=WINDOW_SIZE)
        # )
        # window_std_results.append(
        #     stream_deque.get_window_std(window_size=WINDOW_SIZE)
        # )

        # 空间拓展
        stream_deque.update()
        '''
    window_mean_results = np.array(window_mean_results)
    window_std_results = np.array(window_std_results)

    # one-pass特征抽取
    # *******************
    window_mean_results_onepass = njit_sliding_window_mean(
        df['timestamp'].values,
        df['value'].values,
        WINDOW_SIZE
    )
    window_std_results_onepass = njit_sliding_window_std(
        df['timestamp'].values,
        df['value'].values,
        WINDOW_SIZE
    )

    # 测试
    # *******************
    print('\n***************')
    print('-- MEAN test results: {}'.format(
        np.allclose(window_mean_results, window_mean_results_onepass)
    ))
    print('-- STD test results: {}'.format(
        np.allclose(window_std_results, window_std_results_onepass)
    ))
    print('***************')
    '''