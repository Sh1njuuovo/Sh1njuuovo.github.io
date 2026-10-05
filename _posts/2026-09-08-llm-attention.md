---
title: "第二步笔记：Attention"
date: 2026-09-08 10:00:00 +0800
categories: [大模型]
tags: [LLM 基础]
description: >-
  用公式、形状和代码实验理解注意力、因果遮罩与多头注意力。
math: true
---

[返回大模型学习路线](/posts/llm-foundations/)

> 整理日期：2026-09-08
> 所属路线：[LLM 基础六步学习路线](/posts/llm-foundations/)
> 前置：[Tokenization 与 Embedding](/posts/llm-tokenization-and-embedding/)
> 状态：已整理相关概念，并运行单头 causal self-attention 实验。

## 1. Attention 做什么

Embedding 查表让每个 token 获得初始向量。在同一模型参数下，同一个 token 刚查表时向量相同。

Attention 让每个位置从允许关注的位置读取信息，按不同权重汇总，得到结合上下文的表示。

最核心的操作是：**对各位置的 Value 向量做加权求和。**

假设三个位置提供的信息和某个查询位置分配的权重如下：

| 位置 | Value 向量 | 权重 |
|---|---|---:|
| 我 | `[1, 0]` | 0.1 |
| 喜欢 | `[0, 2]` | 0.2 |
| 苹果 | `[3, 1]` | 0.7 |

这个查询位置的输出是：

$$
o=0.1[1,0]+0.2[0,2]+0.7[3,1]=[2.2,1.1]
$$

如果权重改为 `[0, 1, 0]`，输出就是 `[0, 2]`，全部取自“喜欢”位置。

每个查询位置都有自己的一组权重，因此可以得到不同的输出。

## 2. Query、Key、Value

在 self-attention 中，同一份输入 X 经过三个可学习的线性投影：

$$
Q=XW_Q,\qquad K=XW_K,\qquad V=XW_V
$$

这里省略可能使用的偏置项。同一 head 内，各 token 位置共享这些投影参数。

| 向量 | 作用 | 帮助理解的比喻 |
|---|---|---|
| Query（Q） | 与各位置的 Key 比较 | 我想寻找什么信息 |
| Key（K） | 供 Query 匹配 | 我提供什么线索 |
| Value（V） | 根据权重参与汇总 | 实际被读取的信息 |

比喻仅用于建立直觉；它们实际是训练得到的数值向量。Value 通常是输入经过投影后的结果，不直接等同于原始 token embedding。

### 点积例子

```text
q苹果 = [1, 0]

k我   = [0, 1]
k喜欢 = [2, 0]
k苹果 = [1, 1]
```

得到匹配分数：

```text
[1, 0] · [0, 1] = 0
[1, 0] · [2, 0] = 2
[1, 0] · [1, 1] = 1
```

分数为 `[0, 2, 1]`，“喜欢”最高。

## 3. 从分数到权重：缩放与 Softmax

### 缩放

点积分数除以 Query、Key 维度 d_k 的平方根：

$$
s_{ij}=\frac{q_i\cdot k_j}{\sqrt{d_k}}
$$

这样可以控制点积的尺度，避免维度增大时分数幅度过大，使 softmax 过于集中。

在上面的二维示例中：

```text
[0, 2, 1] / √2 ≈ [0, 1.414, 0.707]
```

### Softmax

对同一个查询位置的所有分数取指数，再归一化：

$$
a_{ij}=\frac{e^{s_{ij}}}{\sum_k e^{s_{ik}}}
$$

```text
缩放分数：[0,     1.414, 0.707]
取指数：  [1,     4.113, 2.028]
权重：    [0.140, 0.576, 0.284]（约）
```

对于有限分数，数学上的 softmax 权重为正，大小顺序与分数一致，权重之和为 1。被 mask 的位置可以获得 0 权重。

若三个分数完全相同，三个权重都是 1/3。

## 4. Causal Mask：遮住未来位置

Decoder-only 模型做 next-token prediction 时，每个位置只能读取自己和前面位置的信息。

例如序列 `我 喜欢 苹果` 中，“喜欢”位置用于预测下一个 token“苹果”。若允许读取后面的“苹果”，就提前看到了目标答案。

| 查询位置 | 读取“我” | 读取“喜欢” | 读取“苹果” |
|---|---|---|---|
| 我 | 允许 | 屏蔽 | 屏蔽 |
| 喜欢 | 允许 | 允许 | 屏蔽 |
| 苹果 | 允许 | 允许 | 允许 |

使用加性 mask M：允许的位置取 0，未来位置取负无穷，在 softmax 前加到分数上。

```text
M = [[0, -∞, -∞],
     [0,  0, -∞],
     [0,  0,  0]]
```

因为 exp(-∞)=0，被屏蔽位置的权重为 0，其余位置重新归一化。

第一个位置只允许读取自己，因此权重为 `[1, 0, 0]`。

## 5. 矩阵形式与形状

完整的单头公式是：

$$
A=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}+M\right),
\qquad O=AV
$$

softmax 沿每一行计算。

- 行：当前哪个位置在查询。
- 列：正在读取哪个位置。
- A 中的第 i 行，是第 i 个位置分配给各位置的权重。

假设有 T 个 token，输入维度为 d_model，单头 Q/K 维度为 d_k，Value 维度为 d_v：

| 张量 | 形状 |
|---|---|
| X | `[T, d_model]` |
| W_Q、W_K | `[d_model, d_k]` |
| W_V | `[d_model, d_v]` |
| Q、K | `[T, d_k]` |
| V | `[T, d_v]` |
| QKᵀ、A | `[T, T]` |
| O=AV | `[T, d_v]` |

Q 和 K 的最后一维需要匹配；Value 的维度可以不同。

在这个例子中，5 个 token、Q/K/V 均为 2 维时，A 是 `[5, 5]`，O 是 `[5, 2]`。

## 6. Multi-head Attention

多个 head 同时处理同一份输入，每个 head 使用自己的 Q/K/V 投影参数，分别计算注意力。

```text
                    输入 X：[5, 4]
                    /           \
              Head 1             Head 2
                 ↓                  ↓
           输出：[5, 2]        输出：[5, 2]
                    \           /
                    沿特征维度拼接
                          ↓
                       [5, 4]
                          ↓
                   输出投影矩阵 W_O
                          ↓
                       [5, 4]
```

$$
\operatorname{MultiHead}(X)
=\operatorname{Concat}(O_1,\ldots,O_h)W_O
$$

- 每个 head 都通过自己的投影读取完整输入向量。
- 不同 head 可以学到不同的匹配与汇总方式，没有预先指定某个 head 必须负责语法或语义。
- 拼接沿特征维度进行，token 数保持不变。
- 输出投影 W_O 对拼接后的特征做线性组合，通常映射回 d_model 维。

在这个例子中，6 个 token、4 个 head、每个 head 输出 8 维，拼接结果为 `[6, 32]`。

## 7. Self-attention 与 Cross-attention

| 类型 | Q 的来源 | K、V 的来源 |
|---|---|---|
| Self-attention | 当前序列 | 同一个序列 |
| Cross-attention | 一个序列 | 另一个序列 |

例如，经典 encoder–decoder 翻译模型可以用目标语言侧的 decoder 表示作为 Q，用源语言侧的 encoder 输出作为 K、V。

“Self”描述来源，“causal”描述允许读取的位置。Decoder-only 中带未来遮罩的自注意力称为 **causal self-attention**。

## 8. 代码实验与实际输出

实验文件：[attention_demo.py](/assets/code/llm/attention_demo.py)。下面保留实验代码，给定 Q/K/V，观察分数、遮罩、权重与输出；该实验不包含学习投影参数、训练或多头计算。

```python
import math
import torch

torch.set_printoptions(precision=3, sci_mode=False)

Q = torch.tensor([
    [1., 0.],
    [0., 1.],
    [1., 1.],
])
K = torch.tensor([
    [1., 0.],
    [0., 1.],
    [1., 1.],
])
V = torch.tensor([
    [1., 0.],
    [0., 2.],
    [3., 1.],
])

d_k = Q.shape[-1]
scores = Q @ K.T / math.sqrt(d_k)
print("① 缩放后的分数，形状：", scores.shape)
print(scores)

future_mask = torch.triu(
    torch.ones(3, 3, dtype=torch.bool), diagonal=1
)
masked_scores = scores.masked_fill(future_mask, float("-inf"))
print("\n② 遮住未来位置后的分数：")
print(masked_scores)

weights = torch.softmax(masked_scores, dim=-1)
print("\n③ 注意力权重：")
print(weights)
print("每行之和：", weights.sum(dim=-1))

output = weights @ V
print("\n④ Attention 输出，形状：", output.shape)
print(output)
```

### 本次实际运行输出

以下结果来自学习时粘贴的本地运行输出：

```text
① 缩放后的分数，形状：torch.Size([3, 3])
tensor([[0.707, 0.000, 0.707],
        [0.000, 0.707, 0.707],
        [0.707, 0.707, 1.414]])

② 遮住未来位置后的分数：
tensor([[0.707,  -inf,  -inf],
        [0.000, 0.707,  -inf],
        [0.707, 0.707, 1.414]])

③ 注意力权重：
tensor([[1.000, 0.000, 0.000],
        [0.330, 0.670, 0.000],
        [0.248, 0.248, 0.503]])
每行之和：tensor([1., 1., 1.])

④ Attention 输出，形状：torch.Size([3, 2])
tensor([[1.000, 0.000],
        [0.330, 1.340],
        [1.759, 1.000]])
```

### 如何读这些结果

1. 第一行权重是 `[1, 0, 0]`，所以第一行输出等于第一个 Value，即 `[1, 0]`。
2. 第二行只读取前两个位置，输出约为 `0.330×[1,0] + 0.670×[0,2] = [0.330,1.340]`。
3. 第三行可以读取全部位置，用第三行权重汇总三个 Value。
4. `dim=-1` 表示沿最后一维计算；在这里就是逐行 softmax。
5. 打印只保留三位小数，第三行显示的权重相加为 0.999 是显示舍入造成的；计算使用更完整的浮点数值。

## 9. 学习记录

- [x] 理解 Value 的加权求和。
- [x] 能计算 Q/K 点积，理解缩放与 softmax。
- [x] 理解 causal mask 的用途和加入位置。
- [x] 能判断注意力矩阵与单头输出的形状。
- [x] 能计算多头拼接后的形状。
- [x] 能区分 self-attention、cross-attention 与 causal 限制。
- [x] 已运行并看懂单头 causal self-attention 实验。

本次学习记录到这里。接着整理 Transformer block 的残差连接、LayerNorm、MLP，以及训练和生成过程。

## 参考材料

- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- [Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY)
- [配套 gpt.py](https://github.com/karpathy/ng-video-lecture/blob/master/gpt.py)
