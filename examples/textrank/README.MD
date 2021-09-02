## TextRank
---
### 简介
利用PageRank算法，对语料中的关键词进行抽取。语料存放于路径`.//data//`路径下。

---
### 系统环境与主要依赖packages
- 系统环境: Ubuntu 18.04 LTS
- GPU: GeForce GTX 1650
- CPU: Intel® Core™ i7-9750H CPU @ 2.60GHz × 12
- RAM: 64G
- python: 3.6.9
- gensim: 3.8.1
- sklearn: 0.23.1
- pandas: 1.0.4
- pkuseg: 0.0.25
- networkx: 2.4

### 进一步的改进
---
* 基于稀疏矩阵的PageRank算法。利用PageRank抽取关键词时，需要构建邻接矩阵，其空间复杂度为*O(n^2)*，其中*n*为结点个数。利用稀疏矩阵对图进行表示，空间复杂度降为*O(n)*。
* 新的PageRank算法。新的PageRank算法可参见文献[1]。
* 利用numba.njit对函数进行加速。即时编译技术可以使得部分函数加速10倍以上，但需要对函数进行处理。

### 参考文献与开源项目
---
[1] Barrios, Federico, et al. "Variations of the similarity function of textrank for automated summarization." arXiv preprint arXiv:1602.03606 (2016).

[2] Mihalcea, Rada, and Paul Tarau. "Textrank: Bringing order into text." Proceedings of the 2004 conference on empirical methods in natural language processing. 2004.

[3] https://github.com/someus/