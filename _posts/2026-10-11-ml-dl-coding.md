---
title: "机器学习与深度学习手撕模板"
date: 2026-10-11 00:00:00 +0800
categories: [算法, 机器学习与深度学习]
tags: [算法手撕, PyTorch]
math: true
description: >-
  10 个带注释的手撕模板，涵盖 Attention、归一化、损失函数、AUC 与 RoPE，说明输入形状和实现边界。
---
这篇整理机器学习与深度学习面试中的代码模板。每节先说明输入输出，再给最小实现和容易出错的地方。代码使用 PyTorch，重点是能解释每一步。

[算法手撕总索引](/posts/algorithm-index/) · [数据结构与算法题目索引](/posts/algorithm-index/#数据结构与算法) · [ACM 输入输出](/posts/acm-python/)

## 模板索引

| 类型 | 模板 | 要点 |
| --- | --- | --- |
| 概率与分类 | [1. Softmax](#1-softmax)、[2. 交叉熵](#2-交叉熵损失) | 数值稳定与真实类别索引 |
| 注意力 | [3. Self-Attention](#3-self-attention)、[4. Multi-Head Attention](#4-multi-head-attention) | QKV 投影、缩放和维度变换 |
| 归一化 | [5. LayerNorm](#5-layernorm)、[6. RMSNorm](#6-rmsnorm) | 最后一维的统计量 |
| 指标 | [7. AUC](#7-auc) | 正负样本比较与同分处理 |
| 检索与排序损失 | [8. InfoNCE](#8-infonce-loss)、[9. BPR](#9-bpr-loss) | 正样本位置、负样本与分数差 |
| 位置编码 | [10. RoPE](#10-rope) | 特征成对旋转 |

本篇沿用本次整理的 10 个模板。代码是面试中的基础版本，省略项会在对应章节说明。

## Attention 输入先问清楚

如果输入已经是 `Q`、`K`、`V`，只需要写缩放点积注意力。如果输入是序列特征 `x`，先用线性层生成 QKV，再计算注意力。

| 版本 | 输入 | 要写的部分 |
| --- | --- | --- |
| 基础 Attention | `Q, K, V` | 点积、缩放、Softmax、加权求和 |
| 完整 Self-Attention | `x`，形状 `[B, L, D]` | QKV 投影和注意力计算 |
| Multi-Head Attention | `x`，形状 `[B, L, D]` | 投影、分头、注意力、拼接和输出投影 |

`B` 是批大小，`L` 是序列长度，`D` 是特征维度。Self-Attention 的 QKV 都由同一份 `x` 投影得到；交叉注意力可以让 Q 来自一个序列，K 和 V 来自另一个序列。

先确认是否需要 QKV 投影、是否需要因果或 Padding Mask，再开始写。

## 统一导入

把某一节单独运行时，先加上这些导入：

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
```

## 十个手撕模板

### 1. Softmax
1
输入浮点张量，沿最后一维计算概率。输出形状不变，每一行的概率和为 `1`。

**数学公式**

对最后一维的分数向量 $x$，令 $m=\max_j x_j$：

$$
p_i=\frac{e^{x_i-m}}{\sum_{j=1}^{C}e^{x_j-m}}.
$$

$C$ 是这一维的长度。减去同一个最大值不改变概率，且能减小指数运算的数值范围。

```python
def softmax(x):
    # 每行减去最大值，避免 exp 溢出
    x = x - x.max(dim=-1, keepdim=True).values
    exp_x = torch.exp(x)
    # keepdim 保留维度，方便广播
    return exp_x / exp_x.sum(dim=-1, keepdim=True)
```

要点是减最大值和 `keepdim=True`。这里假设输入是有限的浮点数。

### 2. 交叉熵损失
2
`logits` 是未经过 Softmax 的分数，形状 `[B, C]`。`labels` 是真实类别下标，形状 `[B]`，类型为 `torch.long`，与 logits 在同一设备上。输出为一个平均损失。

**数学公式**

第 $b$ 个样本的分数为 $z_{b,c}$，真实类别为 $y_b$。令 $m_b=\max_c z_{b,c}$：

$$
\log p_{b,c}=(z_{b,c}-m_b)-\log\sum_{j=1}^{C}e^{z_{b,j}-m_b},
\qquad
\mathcal L=-\frac{1}{B}\sum_{b=1}^{B}\log p_{b,y_b}.
$$

$B$ 是样本数，$C$ 是类别数。代码取真实类别对应的对数概率，再取负值和平均。

```python
def cross_entropy(logits, labels):
    # 先减最大值，再计算 LogSoftmax
    shifted = logits - logits.max(dim=-1, keepdim=True).values
    log_probs = shifted - torch.log(
        torch.exp(shifted).sum(dim=-1, keepdim=True)
    )
    # 每个样本只取真实类别对应的对数概率
    rows = torch.arange(logits.size(0), device=logits.device)
    return -log_probs[rows, labels].mean()
```

这版把 LogSoftmax 展开，方便手写解释。实际调用可用 `F.cross_entropy(logits, labels)`。不要先对 logits 做 Softmax 再传给它。

### 3. Self-Attention
3
输入 `x` 的形状为 `[B, L, D]`，输出同样是 `[B, L, D]`。这个版本包含 QKV 投影，不包含 Mask、Dropout 和额外输出投影。

**数学公式**

令输入 $X\in\mathbb R^{B\times L\times D}$。省略批次下标，线性投影为：

$$
Q=XW_Q+b_Q,\qquad K=XW_K+b_K,\qquad V=XW_V+b_V.
$$

注意力计算为：

$$
A=\operatorname{softmax}_{\mathrm{key}}\left(\frac{QK^\top}{\sqrt{d_k}}+M\right),
\qquad Y=AV.
$$

$d_k$ 是 Q 和 K 的特征维度。基础代码不使用 Mask，相当于 $M=0$。因果 Mask 在允许访问的位置取 $0$，未来位置取 $-\infty$。Softmax 对每个 Query 对应的 Key 分数归一化。

```python
class SelfAttention(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.q = nn.Linear(dim, dim)
        self.k = nn.Linear(dim, dim)
        self.v = nn.Linear(dim, dim)

    def forward(self, x):
        Q = self.q(x)
        K = self.k(x)
        V = self.v(x)
        # [B,L,D] 与 [B,D,L] 相乘，得到 [B,L,L]
        scores = Q @ K.transpose(-2, -1) / math.sqrt(Q.size(-1))
        # 对每个 Query 的全部 Key 归一化
        weights = torch.softmax(scores, dim=-1)
        return weights @ V
```

如果只要求从 QKV 开始，写下面的核心函数即可。Q 和 K 的最后一维相同，K 和 V 的序列长度相同。

```python
def attention(Q, K, V):
    d = Q.size(-1)
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d)
    weights = torch.softmax(scores, dim=-1)
    return weights @ V
```

对于因果注意力，在 Softmax 前把未来位置置为负无穷。下面片段用于 Q、K 等长的自注意力：

```python
L = scores.size(-1)
mask = torch.triu(
    torch.ones(L, L, dtype=torch.bool, device=scores.device),
    diagonal=1,
)
scores = scores.masked_fill(mask, float("-inf"))
weights = torch.softmax(scores, dim=-1)
```

每个 Query 至少要保留一个有效 Key，整行都被屏蔽时 Softmax 会产生 NaN。

### 4. Multi-Head Attention
4
输入输出均为 `[B, L, D]`，`D` 必须能被头数 `H` 整除。每个头的维度是 `d = D // H`。

**数学公式**

设头数为 $H$，每个头的维度为 $d=D/H$。省略批次下标，第 $h$ 个头的计算为：

$$
Q_h=XW_h^Q+b_h^Q,\quad K_h=XW_h^K+b_h^K,\quad V_h=XW_h^V+b_h^V,
$$

$$
\mathrm{head}_h=\operatorname{softmax}_{\mathrm{key}}\left(\frac{Q_hK_h^\top}{\sqrt d}\right)V_h,
$$

$$
Y=\operatorname{Concat}(\mathrm{head}_1,\ldots,\mathrm{head}_H)W_O+b_O.
$$

每个头输出 $L\times d$，拼接后得到 $L\times D$。代码用一次线性投影生成全部 QKV，再通过形状变换分头，最后进行输出投影。

```python
class MHA(nn.Module):
    def __init__(self, dim, heads):
        super().__init__()
        assert heads > 0 and dim % heads == 0
        self.h = heads
        self.d = dim // heads
        self.qkv = nn.Linear(dim, dim * 3)
        self.proj = nn.Linear(dim, dim)

    def forward(self, x):
        B, L, D = x.shape
        # 一次投影后，分成三个 [B,L,D] 张量
        q, k, v = self.qkv(x).chunk(3, dim=-1)

        def split(t):
            # 分头后形状是 [B,H,L,d]
            return t.reshape(B, L, self.h, self.d).transpose(1, 2)

        q, k, v = split(q), split(k), split(v)
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.d)
        weights = torch.softmax(scores, dim=-1)
        y = weights @ v
        # 把头维度移回去，再合并为 [B,L,D]
        y = y.transpose(1, 2).reshape(B, L, D)
        return self.proj(y)
```

缩放使用每个头的维度 `self.d`。这里省略 Mask 和 Dropout；转置后使用 `reshape` 合并维度。

### 5. LayerNorm
5
沿最后一维计算均值和方差，输出形状不变。

**数学公式**

对一个 token 的 $D$ 维特征向量 $x$：

$$
\mu=\frac{1}{D}\sum_{j=1}^{D}x_j,\qquad
\sigma^2=\frac{1}{D}\sum_{j=1}^{D}(x_j-\mu)^2,
$$

$$
\hat x_i=\frac{x_i-\mu}{\sqrt{\sigma^2+\varepsilon}},\qquad
y_i=\gamma_i\hat x_i+\beta_i.
$$

代码返回 $\hat x$，省略了可学习的 $\gamma$ 和 $\beta$。方差分母是 $D$，对应 `unbiased=False`，$\varepsilon$ 用于避免除零。

```python
def layer_norm(x, eps=1e-5):
    mean = x.mean(dim=-1, keepdim=True)
    # 归一化使用总体方差，不做无偏估计
    var = x.var(dim=-1, keepdim=True, unbiased=False)
    return (x - mean) / torch.sqrt(var + eps)
```

这版省略可学习参数 `gamma` 和 `beta`。完整形式是在结果上乘 `gamma`，再加 `beta`。

### 6. RMSNorm
6
沿最后一维计算平方均值，不减均值，输出形状不变。

**数学公式**

对最后一维的 $D$ 个特征：

$$
r=\sqrt{\frac{1}{D}\sum_{j=1}^{D}x_j^2+\varepsilon},\qquad
\hat x_i=\frac{x_i}{r},\qquad y_i=\gamma_i\hat x_i.
$$

代码返回 $\hat x$，省略可学习的缩放参数 $\gamma$。与 LayerNorm 相比，这里直接用平方均值，不减去均值。

```python
def rms_norm(x, eps=1e-6):
    rms = torch.sqrt(x.pow(2).mean(dim=-1, keepdim=True) + eps)
    return x / rms
```

这版省略可学习的缩放参数。混合精度训练中可以用 float32 计算平方均值，再转回原类型。

### 7. AUC
7
`scores` 和 `labels` 都是一维张量，长度相同。标签为 `0` 或 `1`，分数越大表示越倾向正类。

**数学公式**

设正样本分数为 $s_i^+$，负样本分数为 $s_j^-$，数量分别为 $N_+$ 和 $N_-$：

$$
\mathrm{AUC}=\frac{1}{N_+N_-}\sum_{i=1}^{N_+}\sum_{j=1}^{N_-}
\left[\mathbf 1(s_i^+>s_j^-)+\frac12\mathbf 1(s_i^+=s_j^-)\right].
$$

$\mathbf 1(\cdot)$ 表示条件成立时取 $1$，否则取 $0$。正样本分数更高计 $1$，同分计 $0.5$。缺少正样本或负样本时分母为零，因此代码返回 NaN。

```python
def auc(scores, labels):
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    # 只有一种标签时，AUC 无法定义
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    # 比较全部正负样本对，同分算半次正确
    diff = pos[:, None] - neg[None, :]
    return (
        (diff > 0).float().mean()
        + 0.5 * (diff == 0).float().mean()
    ).item()
```

这是便于手写的两两比较版本。时间和额外空间都是 `O(N_pos * N_neg)`。大样本可改用排序与秩统计，把时间降到 `O(N log N)`，同分需要取平均秩。

### 8. InfoNCE Loss
8
`q` 和 `k` 的形状为 `[B, D]`。同下标是一对正样本，其他列作为负样本，温度必须大于 `0`。

**数学公式**

先对向量做 L2 归一化，再计算相似度：

$$
\hat q_i=\frac{q_i}{\max(\lVert q_i\rVert_2,\varepsilon)},\qquad
\hat k_j=\frac{k_j}{\max(\lVert k_j\rVert_2,\varepsilon)},\qquad
z_{ij}=\frac{\hat q_i^\top\hat k_j}{\tau}.
$$

同下标 $(q_i,k_i)$ 是正样本，单向 batch 内负样本损失为：

$$
\mathcal L=-\frac{1}{B}\sum_{i=1}^{B}
\log\frac{e^{z_{ii}}}{\sum_{j=1}^{B}e^{z_{ij}}}.
$$

$\tau>0$ 是温度。每行都把对角线位置当作真实类别，对应代码的 `labels = arange(B)`。归一化分母的保护对应 `F.normalize` 的 `eps`。

```python
def info_nce(q, k, temperature=0.1):
    assert temperature > 0
    # 归一化后，点积就是余弦相似度
    q = F.normalize(q, dim=-1)
    k = F.normalize(k, dim=-1)
    logits = q @ k.T / temperature
    # 第 i 行的正样本是第 i 列
    labels = torch.arange(q.size(0), device=q.device)
    return F.cross_entropy(logits, labels)
```

这是单向、batch 内负样本版本，假设其他下标的样本都可作为负样本。双向版本可以再计算反方向损失，最后取平均。

### 9. BPR Loss
9
`pos_score` 和 `neg_score` 是配对的正负样本分数，形状相同。输出平均损失。

**数学公式**

设第 $i$ 对正负样本分数为 $s_i^+$ 和 $s_i^-$，分数差为 $\Delta_i=s_i^+-s_i^-$：

$$
\sigma(t)=\frac{1}{1+e^{-t}},\qquad
\mathcal L=-\frac{1}{N}\sum_{i=1}^{N}\log\sigma(\Delta_i)
=\frac{1}{N}\sum_{i=1}^{N}\log(1+e^{-\Delta_i}).
$$

$N$ 是配对数量。正样本分数比负样本越高，损失越小。代码使用数值稳定的 `logsigmoid`，没有加入正则项。

```python
def bpr_loss(pos_score, neg_score):
    diff = pos_score - neg_score
    # logsigmoid 避免先 sigmoid 再 log 的数值问题
    return -F.logsigmoid(diff).mean()
```

目标是让正样本分数高于负样本。这里不包含模型参数的正则项。

### 10. RoPE
10
输入浮点张量 `x`，形状 `[B, L, D]`，`D` 为偶数。输出形状不变，位置从 `0` 开始。

**数学公式**

采用从 $0$ 开始的下标。位置为 $p$，相邻维度对的编号为 $j=0,\ldots,D/2-1$：

$$
\omega_j=10000^{-2j/D},\qquad \theta_{p,j}=p\omega_j.
$$

对相邻两个特征进行二维旋转：

$$
\begin{pmatrix}y_{p,2j}\\y_{p,2j+1}\end{pmatrix}
=
\begin{pmatrix}
\cos\theta_{p,j}&-\sin\theta_{p,j}\\
\sin\theta_{p,j}&\cos\theta_{p,j}
\end{pmatrix}
\begin{pmatrix}x_{p,2j}\\x_{p,2j+1}\end{pmatrix}.
$$

代码的 `a`、`b` 分别对应偶数和奇数维度。位置 $p=0$ 时旋转角为零，输出不变。旋转保留每对特征的平方和。

```python
def rope(x):
    B, L, D = x.shape
    assert D % 2 == 0
    pos = torch.arange(L, device=x.device, dtype=torch.float32)
    freq = 1 / (10000 ** (
        torch.arange(0, D, 2, device=x.device, dtype=torch.float32) / D
    ))
    theta = pos[:, None] * freq[None, :]
    cos = theta.cos().to(x.dtype)
    sin = theta.sin().to(x.dtype)
    # 相邻的两个特征维度组成一对
    a = x[..., 0::2]
    b = x[..., 1::2]
    y = torch.stack([
        a * cos - b * sin,
        a * sin + b * cos,
    ], dim=-1)
    return y.flatten(-2)
```

这里采用相邻维度配对。RoPE 通常分别作用于 Q 和 K。不同模型可能采用前后半维度配对，需与模型约定一致。多头张量 `[B, H, L, d]` 可以先把 `B`、`H` 合并后调用此函数，再恢复形状。

## Attention 常见追问

| 问题 | 简短回答 |
| --- | --- |
| 为什么除以平方根维度？ | 在分量方差相近的假设下控制点积尺度，避免 Softmax 过于尖锐 |
| 为什么 Softmax 在最后一维？ | 对每个 Query 对应的全部 Key 归一化 |
| QKV 为什么来自同一份输入？ | 自注意力从同一序列生成查询、键和值 |
| 为什么需要多个头？ | 各个头有独立投影，可以学习不同关系 |
| 为什么需要 Mask？ | 屏蔽 Padding，或在自回归时屏蔽未来位置 |
| 为什么还要输出投影？ | 混合各个头拼接后的特征 |
| 时间复杂度是多少？ | 注意力矩阵计算为 `O(L²D)`，完整模块的线性投影还需 `O(LD²)` |

## 练习顺序

先写 Softmax、交叉熵、LayerNorm 和 RMSNorm，再写 Self-Attention 与 MHA。然后练 AUC、InfoNCE、BPR 和 RoPE。

每次都说明输入形状、输出形状和归一化维度。对 Attention，把投影、分头和矩阵乘法的形状逐步写出来。
