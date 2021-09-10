#!/usr/bin/env python3
#!/usr/local/bin python
# -*- coding: utf-8 -*-

# Created on 202109061216
# Author:     zhuoyin94 <zhuoyin94@163.com>
# Github:     https://github.com/MichaelYin1994

'''
本模块(test_stream_processing.py)用于测试流特征工程的正确性。
'''

import time
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


StreamDeque_kv_ty = (numba.types.int32, numba.types.float64[:])
StreamDeque_spec = [
    ('interval', numba.int32),
    ('max_time_span', numba.int32),
    ('deque_timestamp', numba.int64[:]),
    ('deque_vals', numba.float64[:]),
    ('deque_size', numba.int32),
    ('deque_front', numba.int32),
    ('deque_rear', numba.int32),
    ('deque_stats', numba.types.DictType(*StreamDeque_kv_ty))
]
@jitclass(StreamDeque_spec)
class StreamDeque():
    '''对于时序流数据（stream data）的高效存储与基础特征抽取方法的实现。

    采用numpy array模拟deque，deque保存指定时间区间范围内的时序值。每当时间
    范围不满足条件的时候，通过指针移动模拟队尾元素出队；当array满的时候，
    动态重新分配deque的内存空间。

    我们实现的ArrayDeque在设计时便考虑了数据流时间戳不均匀的问题，通过移动指针
    的方式高效的实现元素的入队和出队，保证deque内只有指定时间范围内的时序数据。

    ArrayDeque的实现中，同时设计了多种针对流数据的特征抽取算法。包括：
    - 给定时间窗口内均值(mean)抽取算法。
    - 给定时间窗口内标准差(std)抽取算法。

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
        用于模拟deque范围的deque的尾指针，永远指向deque最后一个有值元素索引的
        下一个元素索引。
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
            *StreamDeque_kv_ty
        )

        self.deque_timestamp = np.zeros((self.deque_size, ), dtype=np.int64)
        self.deque_vals = np.zeros((self.deque_size, ), dtype=np.float64)
        self.deque_front, self.deque_rear = 0, 0

    def push(self, timestep, x):
        '''将一组元素入队，并且依据deque尾部与首部的元素时间戳，调整deque指针'''
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
        '''若队满，则动态调整队列数组内存空间'''
        if self.is_full():
            rear = len(self.deque_timestamp[self.deque_front:])

            new_deque_timestamp = np.zeros(
                (self.deque_size, ), dtype=np.int64
            )
            new_deque_timestamp[:rear] = self.deque_timestamp[self.deque_front:]
            self.deque_timestamp = new_deque_timestamp

            new_deque_vals = np.zeros(
                (self.deque_size, ), dtype=np.float64
            )
            new_deque_vals[:rear] = self.deque_vals[self.deque_front:]
            self.deque_vals = new_deque_vals

            self.deque_front, self.deque_rear = 0, rear

    def is_full(self):
        '''判断deque是否满'''
        return self.deque_rear >= self.deque_size

    def check_window_size(self, window_size):
        '''检查window_size参数是否合法'''
        if window_size > self.max_time_span or window_size < self.interval:
            raise ValueError('Invalid input window size !')

    def __len__(self):
        return self.deque_rear - self.deque_front

    def get_values(self):
        return self.deque_vals[self.deque_front:self.deque_rear]

    def get_timestamp(self):
        return self.deque_timestamp[self.deque_front:self.deque_rear]

    def get_window_mean(self, window_size=120):
        '''抽取window_size范围内的mean统计量'''
        self.check_window_size(window_size)

        # 载入stream参数
        field_name = hash(window_size) + 0

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
        new_params = np.array(
            [dist2end, window_sum], dtype=np.float64
        )
        self.deque_stats[field_name] = new_params

        return mean_res

    def get_window_std(self, window_size=120):
        '''抽取window_size范围内std统计量'''
        self.check_window_size(window_size)

        # 载入stream参数
        field_name = hash(window_size) + 1

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
        new_params = np.array(
            [dist2end, window_sum, window_squre_sum], dtype=np.float64
        )
        self.deque_stats[field_name] = new_params

        return mean_res

    def get_window_shift(self, n_shift):
        '''抽取当前时刻给定上n_shift个时刻的数据的值'''
        if n_shift > (self.deque_rear - self.deque_front):
            return np.nan
        else:
            return self.deque_vals[self.deque_rear - 1]

    def get_window_range_count(self, window_size, low, high):
        '''抽取window_size内的位于low与high闭区间内部数据的比例'''
        # 输入检查
        if low > high:
            raise ValueError('Invalid value range !')
        self.check_window_size(window_size)

        # 载入stream参数
        field_name = hash(window_size) + hash(low) + hash(high)

        if field_name in self.deque_stats:
            dist2end, low_count, high_count = self.deque_stats[field_name]
        else:
            low_count, high_count = 0, 0
            dist2end = self.deque_rear - self.deque_front - 1

        start = int(self.deque_rear - dist2end - 1)
        end = int(self.deque_rear - 1)

        # 重新计算参数
        dist2end, low_count, high_count = self.compute_window_range_count(
            self.deque_timestamp,
            self.deque_vals,
            start, end, low, high,
            low_count, high_count, window_size
        )

        # 更新预置参数
        new_params = np.array(
            [dist2end, low_count, high_count], dtype=np.float64
        )
        self.deque_stats[field_name] = new_params
        count_res = (dist2end - low_count - high_count) / dist2end

        return count_res

    def get_window_hog_1d(self, window_size, low, high, n_bins):
        '''抽取window_size内的1-D Histogram of Gradient统计量'''
        # 输入检查
        if n_bins <= 0:
            raise ValueError('Invalid n_bins !')
        elif low < -90 or high > 90 or low > high:
            raise ValueError('Invalid low or high value !')
        self.check_window_size(window_size)

        # 载入stream参数
        field_name = hash(window_size) + hash(n_bins) + hash(low) + hash(high)

        if field_name in self.deque_stats:
            bin_count_meta = self.deque_stats[field_name]
            dist2end, bin_count = bin_count_meta[0], bin_count_meta[1:]
        else:
            bin_count = np.zeros((n_bins, ), dtype=np.float64)
            dist2end = self.deque_rear - self.deque_front - 1

        start = int(self.deque_rear - dist2end - 1)
        end = int(self.deque_rear - 1)

        # 重新计算参数
        dist2end, bin_count = self.compute_window_degree_bin_count(
            self.deque_timestamp,
            self.deque_vals,
            start, end, low, high,
            bin_count, self.interval, window_size
        )

        # 更新预置参数
        new_params = np.hstack(
            (np.array([dist2end], dtype=np.float64),
             bin_count.astype(np.float64))
        )
        self.deque_stats[field_name] = new_params
        count_res = bin_count / dist2end

        return count_res

    def get_window_weighted_mean(self, window_size, weight_array):
        '''计算指定window_size内的带权平均值'''
        pass

    def get_exponential_weighted_mean(self, window_size, alpha):
        '''抽取给定window_size内的EWMA加权结果'''
        pass

    def get_window_max(self):
        pass

    def get_window_min(self):
        pass

    def compute_window_degree_bin_count(self, timestamp, sensor_vals,
                                        start, end, low, high,
                                        bin_count, interval, max_time_span):
        # 生成histogram窗口边界
        bin_range = np.linspace(low, high, len(bin_count) + 1)

        # 计算当前样本的Gradient
        y_delta = (sensor_vals[end] - sensor_vals[max(end-1, 0)])
        x_delta = (timestamp[end] - timestamp[max(end-1, 0)]) / interval
        if x_delta == 0:
            degree= 0
        else:
            degree = np.rad2deg(np.arctan(y_delta / x_delta))

        # 将Gradient映射到bin上去
        for i in range(1, len(bin_count) + 1):
            if degree > bin_range[i-1] and degree <= bin_range[i]:
                bin_count[i-1] += 1
                break

        # 时间窗口放缩，统计量修正
        time_gap = timestamp[end] - timestamp[start]

        if time_gap > max_time_span:
            while(start <= end and time_gap > max_time_span):

                # 统计量更新
                y_delta = (sensor_vals[min(end, start+1)] - sensor_vals[start])
                x_delta = (timestamp[min(end, start+1)] - timestamp[start]) / interval
                if x_delta == 0:
                    degree= 0
                else:
                    degree = np.rad2deg(np.arctan(y_delta / x_delta))

                for i in range(1, len(bin_count) + 1):
                    if degree > bin_range[i-1] and degree <= bin_range[i]:
                        bin_count[i-1] -= 1
                        break

                start += 1
                time_gap = timestamp[end] - timestamp[start]
        dist2end = end - start + 1

        return dist2end, bin_count

    def compute_window_range_count(self, timestamp, sensor_vals,
                                   start, end, low, high,
                                   low_count, high_count, max_time_span):
        # 时间窗口放缩，统计量修正
        window_low_count_delta = 0
        window_high_count_delta = 0
        time_gap = timestamp[end] - timestamp[start]

        if sensor_vals[end] > high:
            high_count += 1
        elif sensor_vals[end] < low:
            low_count += 1

        if time_gap > max_time_span:
            while(start <= end and time_gap > max_time_span):
                if sensor_vals[start] > high:
                    window_high_count_delta -= 1
                elif sensor_vals[start] < low:
                    window_low_count_delta -= 1
                start += 1
                time_gap = timestamp[end] - timestamp[start]

        # 统计量更新
        dist2end = end - start + 1
        low_count = low_count + window_low_count_delta
        high_count = high_count + window_high_count_delta

        return dist2end, low_count, high_count

    def compute_window_std(self, timestamp, sensor_vals,
                           start, end, window_sum, window_squre_sum,
                           max_time_span):
        if np.isnan(window_sum):
            window_sum = np.sum(sensor_vals[start:(end + 1)])
            window_squre_sum = np.sum(sensor_vals[start:(end + 1)]**2)
        else:
            window_sum += sensor_vals[end]
            window_squre_sum += sensor_vals[end]**2

        # 时间窗口放缩，统计量修正
        window_sum_delta = 0
        window_squre_sum_delta = 0
        time_gap = timestamp[end] - timestamp[start]

        if time_gap > max_time_span:
            while(start <= end and time_gap > max_time_span):
                window_sum_delta -= sensor_vals[start]
                window_squre_sum_delta -= sensor_vals[start]**2
                start += 1
                time_gap = timestamp[end] - timestamp[start]

        # 统计量更新
        dist2end = end - start + 1
        window_sum = window_sum + window_sum_delta
        window_squre_sum = window_squre_sum + window_squre_sum_delta
        std_res = np.sqrt(
            window_squre_sum / dist2end - (window_sum / dist2end)**2
        )

        return dist2end, window_sum, window_squre_sum, std_res

    def compute_window_mean(self, timestamp, sensor_vals,
                            start, end, window_sum,
                            max_time_span):
        if np.isnan(window_sum):
            window_sum = np.sum(sensor_vals[start:(end + 1)])
        else:
            window_sum += sensor_vals[end]

        # 时间窗口放缩，统计量修正
        window_sum_delta = 0
        time_gap = timestamp[end] - timestamp[start]

        if time_gap > max_time_span:
            while(start <= end and time_gap > max_time_span):
                window_sum_delta -= sensor_vals[start]
                start += 1
                time_gap = timestamp[end] - timestamp[start]

        # 统计量更新
        dist2end = end - start + 1
        window_sum = window_sum + window_sum_delta
        mean_res = window_sum / dist2end

        return dist2end, window_sum, mean_res


if __name__ == '__main__':
    # 生成kpi仿真数据（单条kpi曲线）
    # *******************
    N_POINTS = 3000000
    MIN_INTERVAL = 20
    MAX_TIME_SPAN = int(5 * 24 * 3600)
    WINDOW_SIZE = int(6 * 3600)
    df = generate_simulation_data(n_points=N_POINTS, min_interval=MIN_INTERVAL)
    df['value'] = (df['value'] - df['value'].mean()) / df['value'].std()

    # 流式抽取统计特征
    # *******************
    stream_deque = StreamDeque(
        interval=MIN_INTERVAL, max_time_span=MAX_TIME_SPAN
    )

    window_mean_results = []
    window_std_results = []
    window_shift_results = []
    window_count_results = []
    window_hog_1d_results = []
    for timestep, sensor_val in tqdm(df[['timestamp', 'value']].values):
        # 元素入队
        stream_deque.push(timestep, sensor_val)

        # 统计量计算
        window_mean_results.append(
            stream_deque.get_window_mean(WINDOW_SIZE)
        )

        window_std_results.append(
            stream_deque.get_window_std(WINDOW_SIZE)
        )

        window_count_results.append(
            stream_deque.get_window_range_count(
                WINDOW_SIZE, 0.2, 0.5
            )
        )

        window_hog_1d_results.append(
            stream_deque.get_window_hog_1d(
                WINDOW_SIZE, -60, 60, 16
            )
        )
        # 空间拓展
        stream_deque.update()
