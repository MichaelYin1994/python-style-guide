## 2018年AIOps国际挑战赛数据集基线方法

---
### **作者简介**

作者：鱼丸粗面（zhuoyin94@163.com）。整体采用了[此项目](https://github.com/MichaelYin1994/python-style-guide)的编码规范。**注意！**本项目对内存要求较大（32G+），Linux环境下需要更大的swap空间支持！（20210831）

---
### **系统环境依赖**

- 系统环境: Ubuntu 20.04 LTS
- GPU: NVIDIA Corporation GP104GL [Quadro P5000](16G)
- CPU: Intel® Core™ i9-9920X CPU @ 3.50GHz × 24
- RAM: 94G
- CUDA: 10.1
- swap: 64G
- python == 3.6.9
- pandas == 1.0.4
- numba == 0.49.0
- numpy == 1.18.1
- xgboost == 1.2.1
- scikit-learn == 0.22.2
- scipy == 1.4.1
- tensorflow-gpu == 2.5.0

---
### **代码与存储结构**

```
.
├── cached_data
│   ├── test_df_part_x.pkl
│   ├── test_df_part_y.pkl
│   ├── test_df.pkl
│   ├── train_df.pkl
│   └── train_feats_list.pkl
├── data
│   ├── kpi competition
│   │   ├── phase2_ground_truth.hdf
│   │   └── phase2_train.csv
│   └── zips
│       ├── KPI异常检测决赛数据集.zip
│       └── train.zip
├── logs
│   └── logs.csv
├── models
│   └── models.pkl
├── README.MD
└── src
    ├── test
    │   ├── test_stream_data.py
    │   └── test_utils.py
    ├── compute_feature_engineering.py
    ├── create_train_test.py
    ├── evaluation.py
    ├── exploring_data.py
    ├── offline_inference.py
    ├── online_inference.py
    ├── train_lightgbm.py
    ├── train_nn.py
    ├── train_xgboost.py
    └── utils.py
```

文档结构：
- **./cached_data/**: 用于存储原始数据简单预处理后的临时数据，以及训练数据特征工程的结果。
- **./data/**: 用于存储原始比赛数据（Raw data）。
- **./logs/**: 训练/Online serving阶段的日志记录。
- **./models/**: 训练好的模型文件位置。
- **./src/**: 项目源码。
- **./src/test/**: 项目单元测试与Online serving流测试。

主要代码文件说明：
- **./src/create_train_test.py**: 简单预处理原始数据，并且拆分测试集，并构造流测试数据集。
- **./src/compute_feature_engineering.py**: 高性能流特征工程。
- **./src/train_lightgbm.py**: CPU环境训练LightGBM模型。
- **./src/train_xgboost.py**: GPU环境训练XGBoost模型。
- **./src/train_nn.py**: GPU环境训练Tabular Neural Network模型。
- **./src/offline_inference.py**: 使用训练好的模型，对测试数据或者部分测试数据执行离线推理。

---
### **References**

[1] https://github.com/MichaelYin1994/tianchi-pakdd-aiops-2021

[2] Lam, Siu Kwan, Antoine Pitrou, and Stanley Seibert. "Numba: A llvm-based python jit compiler." Proceedings of the Second Workshop on the LLVM Compiler Infrastructure in HPC. 2015.

[3] https://github.com/johannfaouzi/pyts

[4] https://github.com/blue-yonder/tsfresh

[5] Goldstein M, Dengel A. Histogram-based outlier score (hbos): A fast unsupervised anomaly detection algorithm[J]. KI-2012: Poster and Demo Track, 2012: 59-63.

[6] Bu, Jiahao, et al. "Rapid deployment of anomaly detection models for large number of emerging kpi streams." 2018 IEEE 37th International Performance Computing and Communications Conference (IPCCC). IEEE, 2018.

[7] Ma M, Zhang S, Pei D, et al. Robust and rapid adaption for concept drift in software system anomaly detection[C]//2018 IEEE 29th International Symposium on Software Reliability Engineering (ISSRE). IEEE, 2018: 13-24.

[8] Li, Zhihan, et al. "Robust and rapid clustering of kpis for large-scale anomaly detection." 2018 IEEE/ACM 26th International Symposium on Quality of Service (IWQoS). IEEE, 2018.

[9] Li, Zeyan, Wenxiao Chen, and Dan Pei. "Robust and unsupervised kpi anomaly detection based on conditional variational autoencoder." 2018 IEEE 37th International Performance Computing and Communications Conference (IPCCC). IEEE, 2018.

[10] Liu, Dapeng, et al. "Opprentice: Towards practical and automatic anomaly detection through machine learning." Proceedings of the 2015 Internet Measurement Conference. 2015.

[11] Zhao, Nengwen, et al. "Label-less: A semi-automatic labelling tool for kpi anomalies." IEEE INFOCOM 2019-IEEE Conference on Computer Communications. IEEE, 2019.

