---
title: "第六步笔记：RoPE、GQA 与生成式推荐"
date: 2026-09-10 10:00:00 +0800
categories: [大模型]
tags: [LLM 基础]
description: >-
  从 RoPE 与 GQA 出发，衔接物品编码和生成式推荐。
math: true
---

[返回大模型学习路线](/posts/llm-foundations/)

> 整理日期：2026-09-10
> 所属路线：[LLM 基础六步学习路线](/posts/llm-foundations/)
> 前置：[预训练、SFT、RL 与 DPO](/posts/llm-pretraining-sft-and-rl/)
> 状态：本轮入门概念讲解已完成；未实现 RoPE、GQA 或推荐模型，未完成对应论文精读。

## 1. RoPE：按位置旋转 Q、K

小 GPT 使用可学习的位置 embedding，与 token embedding 相加：

```python
x = token_embedding + position_embedding
```

RoPE（Rotary Position Embedding，旋转位置编码）则根据位置旋转 Attention 中的 Q、K。标准用法不对 V 做这种旋转。

### 二维直觉

```text
位置 0：旋转 0θ
位置 1：旋转 1θ
位置 2：旋转 2θ
```

实际将向量维度两两配对，每对使用自己的旋转频率。二维旋转可写为：

$$
R(\phi)=\begin{bmatrix}
\cos\phi&-\sin\phi\\
\sin\phi&\cos\phi
\end{bmatrix}
$$

### 为什么能体现相对位置

令 q_i、k_j 为旋转前的向量，R_i、R_j 为对应位置的旋转矩阵。标准 RoPE 满足：

$$
(R_iq_i)^\top(R_jk_j)
=q_i^\top R_i^\top R_jk_j
=q_i^\top R_{j-i}k_j
$$

位置影响通过相对距离 j−i 体现。例如位置 2 与 5、位置 7 与 10 都相距 3；若旋转前的对应 Q/K 相同，两组旋转后的点积相同。

真实模型的 Q/K 还依赖内容与上下文，因此距离相同不保证注意力分数相同。

### 与 Causal Mask 的区别

- RoPE 给匹配分数引入位置信息。
- Causal mask 限制哪些位置可被读取。
- 使用 RoPE 仍需 causal mask，旋转本身不会屏蔽未来。

## 2. RoPE 与 KV Cache

常见实现中，每层缓存已按位置旋转的 K，以及 V。

假设“我 喜欢 苹果”位于 0、1、2，下一轮加入位置 3 的“手机”：

```text
计算新 token 在当前层的 q₃、k₃、v₃
                    ↓
按位置 3 旋转 q₃、k₃
                    ↓
将旋转后的 k₃ 和 v₃ 追加到当前层缓存
                    ↓
用旋转后的 q₃ 查询所有缓存的 K，汇总 V
```

固定位置规则下，旧 K 保留原来的旋转结果，不因追加 token 而重新旋转。新 Query 与旧 Key 的点积体现二者相对位置。

这里讨论标准固定 RoPE 设置；涉及动态位置缩放或缓存重定位时，应以具体实现为准。

## 3. GQA：多个 Query Head 共享 KV

GQA（Grouped-Query Attention，分组查询注意力）的动机是减少 KV Cache 大小与生成时的缓存读取开销。

以 8 个 Query head 为例：

| 结构 | Query head 数 | KV head 数 | 共享方式 |
|---|---:|---:|---|
| MHA | 8 | 8 | 每个 Q head 对应自己的 KV |
| GQA 示例 | 8 | 2 | 每 4 个 Q head 共享一组 KV |
| MQA | 8 | 1 | 所有 Q head 共享一组 KV |

```text
Q₁、Q₂、Q₃、Q₄ → 共享 K₁、V₁
Q₅、Q₆、Q₇、Q₈ → 共享 K₂、V₂
```

共享 K/V 不要求输出相同：各 Query 可以产生不同的权重，进而得到不同的加权汇总结果。这一点已正确复述。

在层数、长度、head 维度和数据类型相同时，上述 GQA 缓存约为 MHA 的 2/8=1/4。不代表整个模型内存或推理耗时也降到四分之一。

在 K/V 每个 head 都为 d_h 维时，缓存元素量可近似写成：

$$
2\times B\times L\times T\times H_{KV}\times d_h
$$

其中 2 对应 K 与 V，B 为 batch 大小，L 为层数，T 为缓存长度，H_KV 为 KV head 数。乘以每个元素的字节数得到理想数据存储量，不包含分配与管理开销。

**KV Cache 复用历史结果，GQA 减少需要缓存的 KV head 数。**

## 4. 从文本 Token 到物品 ID

一种直接方案是每个物品对应一个独立 ID：

```text
物品 A → 103
物品 B → 825
物品 C → 291

用户历史：[103, 825, 291]
目标：预测下一个物品
```

这与 next-token prediction 共享序列预测的思路。物品数量大时，直接使用完整物品词表会带来较大的 embedding 表和输出空间。

## 5. Semantic ID：一个物品对应多个离散编码

Semantic ID 可以通过量化物品向量等方法构造，将一个物品表示为多个离散编码。

教学示例：

```text
物品 A → [12, 7, 3]
物品 B → [12, 7, 9]
物品 C → [25, 4, 2]
```

推荐 A 可以变为自回归生成 12、7、3，再映射回物品 A。示例中的数字只用于解释；实现可能为不同编码层使用不同 token 空间或偏移。

- Semantic ID 的构造与文本 BPE 不同。
- 相似物品可能共享编码前缀，但效果取决于物品表示和编码训练方式。
- 不同物品可能发生编码碰撞，需要消歧或唯一性设计。
- 缩小每步输出空间的同时，会增加生成步骤；具体效率需结合实现评价。

## 6. 推荐训练：学习生成下一个物品的编码

用户历史 A→B，真实下一个物品为 C：

| 给定内容 | 正确下一个编码 |
|---|---:|
| 历史 A→B | 25 |
| 历史 A→B，加上 25 | 4 |
| 历史 A→B，加上 25、4 | 2 |

令 H 为用户历史，若编码唯一映射到 C：

$$
P(C\mid H)
=P(25\mid H)P(4\mid H,25)P(2\mid H,25,4)
$$

对应负 log 概率损失：

$$
L=-\log P(25\mid H)
-\log P(4\mid H,25)
-\log P(2\mid H,25,4)
$$

即熟悉的 next-token 交叉熵。该式针对固定三段编码示例，省略可能的结束标记与归一化。

训练时真实编码前缀已给出，可以使用 teacher forcing。历史如何编码取决于方法，可以采用 encoder–decoder 或 decoder-only 等结构。

## 7. Constrained Decoding：只生成合法编码

模型可能生成 `[12, 4, 8]`，但物品库中没有这个编码。可以用 Trie（前缀树）限制允许扩展的 token：

```text
开始
├─ 12
│  └─ 7
│     ├─ 3 → 物品 A
│     └─ 9 → 物品 B
└─ 25
   └─ 4
      └─ 2 → 物品 C
```

生成到 `[12, 7]` 时，只允许选择 3 或 9，其余候选被屏蔽。

约束保证在正确实现、完成合法终止路径时得到编码库中的物品；它不保证物品一定适合用户。编码碰撞、物品上下架等仍需处理。

### 与 Beam Search 配合

```text
用户历史
   ↓
Beam Search + 合法前缀约束
   ↓
多条完整物品编码
   ↓
映射物品、去重、按任务要求过滤
   ↓
Top-K 推荐列表
```

Beam width 与最终推荐数量 K 是不同参数。去重、过滤、搜索结束规则都会影响最终候选数量。

是否过滤已交互物品取决于任务；有些场景允许重复消费，不能统一排除。

## 8. 评价：HR@K 与 NDCG@K

以下公式适用于每条测试样本只有一个真实目标物品的情况。

### HR@K

目标物品出现在前 K 个推荐中记为 1，否则为 0，再对测试样本取平均。

### NDCG@K

若目标排名为 r（从 1 开始）：

$$
\operatorname{NDCG@K}=
\begin{cases}
1/\log_2(r+1), & r\le K\\
0, & r>K\text{ 或未出现}
\end{cases}
$$

最后对测试样本取平均。多个相关物品或分级相关性时，需要使用完整 DCG/IDCG 定义。

真实物品为 C：

```text
[C, A, B]：命中，排名最好
[A, B, C]：同样命中，但 NDCG 更低（K≥3 时）
```

比较实验时，需要一致的候选集合、数据划分和过滤规则；完整物品库与负采样候选上的指标不能直接混比。

## 9. 学习状态

- [x] 已讲解 RoPE 的旋转直觉、相对位置关系及与 causal mask 的区别。
- [x] 已讲解 RoPE 与 KV Cache 的连接。
- [x] 已理解 GQA 共享 KV，且不同 Q 仍可产生不同输出。
- [x] 已讲解 item ID 与 Semantic ID 的区别。
- [x] 已讲解物品编码的自回归训练、Trie 约束与 Beam Search。
- [x] 已讲解单目标 HR@K、NDCG@K。
- [ ] RoPE／GQA 代码实现、推荐实验与论文精读：尚未进行。

六步路线的入门讲解已覆盖。后续进入推荐论文，将这些概念对应到具体模型、数据和评估协议，继续按需补齐。

## 后续阅读材料

- [RoPE / RoFormer](https://arxiv.org/abs/2104.09864)：旋转位置编码。
- [GQA](https://arxiv.org/abs/2305.13245)：Query head 与 KV head 的分组共享。
- [TIGER](https://arxiv.org/abs/2305.05065)：物品语义编码与生成式检索。

以上为路线中的后续阅读入口，本笔记不代表已完成这些论文的精读与结果核验。
