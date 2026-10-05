---
title: "第三步笔记：Transformer 与 Decoder-only LLM"
date: 2026-09-09 10:00:00 +0800
categories: [大模型]
tags: [LLM 基础]
description: >-
  梳理 Transformer block、decoder-only 语言模型、训练目标和逐 token 生成。
math: true
---

[返回大模型学习路线](/posts/llm-foundations/)

> 整理日期：2026-09-08
> 所属路线：[LLM 基础六步学习路线](/posts/llm-foundations/)
> 前置：[Attention](/posts/llm-attention/)
> 状态：已整理核心概念，并运行小 GPT 实验。
> 实验代码：[mini_gpt_demo.py](/assets/code/llm/mini_gpt_demo.py)

## 1. 从 Attention 到完整模型

```text
文本 → tokenizer → token IDs
                     ↓
            token embedding + 位置信息
                     ↓
             Transformer block × N
                     ↓
               最后的 LayerNorm
                     ↓
                   LM head
                     ↓
                   logits
                 /        \
       与真实标签计算损失    取最后位置，选择下一个 token
              ↓                       ↓
          更新参数                追加到输入并继续
```

本轮的小 GPT 使用一个 Pre-LN block、可学习的位置 embedding 和 ReLU MLP。它用于学习数据流，不代表所有现代 LLM 都采用相同配置。

## 2. 残差连接：保留输入，学习调整量

残差连接将子层输出与输入逐元素相加：

$$
Y=X+F(X)
$$

例如：

```text
输入 x：     [1.0,  2.0, 3.0]
分支输出：   [0.2, -0.5, 0.1]
相加结果：   [1.2,  1.5, 3.1]
```

分支可以学习对已有表示的调整量；输入保留直接到达输出的路径，有利于深层网络的信息和梯度传播。

- 本例中输入与分支输出形状一致，才能按预期逐元素相加。
- 若 X 是 `[5, 32]`，分支输出也是 `[5, 32]`。
- 若分支输出全为 0，结果就是 X。

这两个例子说明残差相加需要形状一致，且零分支输出会保留输入。

## 3. LayerNorm：对每个 token 的特征归一化

对一个 token 的 d 维向量 x，LayerNorm 使用这个向量内部的均值与方差：

$$
\mu=\frac{1}{d}\sum_{j=1}^{d}x_j,
\qquad
\sigma^2=\frac{1}{d}\sum_{j=1}^{d}(x_j-\mu)^2
$$

$$
\operatorname{LN}(x)
=\gamma\odot\frac{x-\mu}{\sqrt{\sigma^2+\epsilon}}+\beta
$$

- ε 是数值稳定项。
- γ、β 是可学习的逐维缩放与偏移参数，各 token 位置共享。
- 归一化有助于稳定后续计算与训练。
- LayerNorm 不改变形状。

例如输入：

```text
[[ 1,  2,  3],
 [10, 20, 30]]
```

每一行独立计算均值与方差。忽略 ε，且 γ=1、β=0 时，两行都归一化为约 `[-1.225, 0, 1.225]`。应用可学习的缩放与偏移后，不必再具有零均值和单位方差。

对 `[5, 32]`，在每个 token 的 32 个维度上统计，输出仍是 `[5, 32]`。

## 4. MLP / FFN：逐位置非线性变换

MLP 对每个位置的向量独立做非线性变换，各位置共享同一套参数。

```text
[5, 32]
   ↓ Linear：32 → 128
[5, 128]
   ↓ ReLU
[5, 128]
   ↓ Linear：128 → 32
[5, 32]
```

一般可写为：

$$
\operatorname{MLP}(x)=\phi(xW_1+b_1)W_2+b_2
$$

- Attention 直接在不同 token 位置之间汇总信息。
- MLP 在每个位置上处理特征，不直接混合不同位置。
- 中间维度扩展到 4 倍是本例配置，可以调整。
- 激活函数提供非线性；若去掉激活，两层连续的仿射变换可合并为一层。

## 5. 完整的 Pre-LN Transformer Block

$$
Y=X+\operatorname{Attention}(\operatorname{LN}_1(X))
$$

$$
Z=Y+\operatorname{MLP}(\operatorname{LN}_2(Y))
$$

```text
X ─────────────────────┐
↓                      │
LayerNorm → Attention  │
↓                      │
相加 ←─────────────────┘
↓ Y
├──────────────────────┐
↓                      │
LayerNorm → MLP        │
↓                      │
相加 ←─────────────────┘
↓ Z
```

对应代码：

```python
x = x + self.sa(self.ln1(x))
x = x + self.ffwd(self.ln2(x))
```

一个 block 有两个子层、两次残差连接。输入 `[6, 32]`，输出仍是 `[6, 32]`。已独立回答正确，并正确识别 Attention 负责跨位置汇总信息。

## 6. 位置表示与 Decoder-only

本例用可学习的位置 embedding 表示第 0、1、2……个位置，再与 token embedding 相加：

```python
positions = torch.arange(T, device=ids.device)
x = self.token_emb(ids) + self.position_emb(positions)
```

Token embedding 形状是 `[B, T, d]`，位置 embedding 是 `[T, d]`，相加时沿 batch 维广播。它让模型获得显式的位置线索。RoPE 使用另一种注入位置信息的方法，后续再学。

本例使用 causal self-attention，没有单独的 encoder 或 cross-attention，属于 decoder-only 架构。

作为对照：encoder 常用于对输入进行双向编码；经典 encoder–decoder 模型先编码源序列，再由 decoder 通过 causal self-attention 和对 encoder 输出的 cross-attention 生成目标序列。这里只记录架构对照，尚未进一步展开。

## 7. LM Head、Logits 与词表

经过 blocks 和最后的 LayerNorm，隐藏表示为 `[B, T, d]`。LM head 将每个位置的 d 维向量映射到 V 个词表分数：

$$
\text{logits}=HW_{\text{out}}+b,
\qquad W_{\text{out}}\in\mathbb{R}^{d\times V}
$$

这是数学上的矩阵记法；PyTorch `nn.Linear(d, V)` 内部权重存储形状为 `[V, d]`。

```text
隐藏表示：[B, T, d]
    ↓ LM head
logits： [B, T, V]
```

例如 5 个 token、隐藏维度 32、词表大小 100，不计 batch 时 logits 是 `[5, 100]`。

**Logits 是分数，可以为正或负；沿词表维度做 softmax 后，才是预测概率。** 每一行都在预测紧接该位置的下一个 token。

### 与 tokenizer 词表的关系

输出候选通过 token ID 与配套 tokenizer 的词表对齐：

```text
输入：“猫” → ID 2 → 取 embedding 矩阵第 2 行
输出：logits 第 2 列 → 下一个 token 为“猫”的分数
```

输入只用了几个 token，输出仍然对整个候选词表打分。词表不会为每个输入重新建立。工程模型还可能包含特殊 token 或为对齐预留的槽位，应以具体配置为准。

| 部分 | 数学形状 | 作用 |
|---|---|---|
| 输入 embedding | `[V, d]` | 按 ID 查向量 |
| 输出投影 | `[d, V]` | 将隐藏向量变成候选分数 |

词表 ID 对齐不要求两者共享参数；有些模型通过 weight tying 共享权重，本实验未共享。

## 8. 训练：标签向后错一位

原始序列：

```text
我 喜欢 苹果 手机 <结束>
```

构造输入与标签：

| 输入位置 | 可见上下文 | 正确标签 |
|---|---|---|
| 我 | 我 | 喜欢 |
| 喜欢 | 我 喜欢 | 苹果 |
| 苹果 | 我 喜欢 苹果 | 手机 |
| 手机 | 我 喜欢 苹果 手机 | <结束> |

```python
inputs = sequence[:, :-1]
targets = sequence[:, 1:]
```

以 `[12, 5, 8, 3, 9]` 为例，输入为 `[12, 5, 8, 3]`，标签为 `[5, 8, 3, 9]`。

训练输入的真实 token 已经给出，causal mask 又能防止读取未来，因此可以一次计算各位置的预测，无需先生成前一个位置的答案。

### 交叉熵

单个位置的损失为：

$$
L_t=-\ln p(x_{t+1}\mid x_{\le t})
$$

正确标签的概率为 0.1 时，损失约 2.303；为 0.8 时，约 0.223。概率越高，损失越小。通常对有效位置取平均。

```python
loss = F.cross_entropy(
    logits.reshape(-1, V),
    targets.reshape(-1),
)
```

交叉熵接收 logits，内部完成相应的归一化计算，无需事先手动 softmax。

```text
logits：[B, T, V] → [B×T, V]
标签：  [B, T]    → [B×T]
```

每个位置成为一道 V 选一的预测题。随后：

```python
optimizer.zero_grad()
loss.backward()
optimizer.step()
```

依次清空旧梯度、反向传播计算梯度、由优化器更新参数。

## 9. 生成：使用最后位置的输出，逐 token 追加

输入 `我 喜欢 苹果` 时：

```text
“我”位置的输出：预测第 2 个 token
“喜欢”位置的输出：预测第 3 个 token
“苹果”位置的输出：预测第 4 个 token ← 续写使用这一行
```

前面的输入已经确定，续写需要预测当前序列之后的 token，因此取最后位置。

```python
last_logits = logits[:, -1, :]              # [B, V]
next_id = last_logits.argmax(-1, keepdim=True)  # [B, 1]
ids = torch.cat([ids, next_id], dim=1)       # [B, T+1]
```

这里使用 greedy decoding，直接取最高分 ID；softmax 保持大小顺序，所以取 argmax 无需先算概率。

```text
我 喜欢
   ↓ 选出“苹果”并追加
我 喜欢 苹果
   ↓ 再预测一个 token
我 喜欢 苹果 手机
```

普通推理固定参数，输入序列每轮增长，不执行反向传播和优化器更新。该区别已回答正确。

- `model.eval()` 切换 Dropout 等模块的训练／推理行为，本身不关闭梯度。
- `torch.no_grad()` 关闭梯度记录。
- 本实验每轮重新计算完整前缀，没有使用 KV cache。

## 10. 本地小 GPT 实验

代码见 [mini_gpt_demo.py](/assets/code/llm/mini_gpt_demo.py)。实验配置：

- 词表大小 10，隐藏维度 16。
- 一个 Pre-LN block，两个 attention head。
- MLP 中间维度 64，激活函数为 ReLU。
- 可学习的位置表支持 16 个位置。
- 随机初始化，在一条示例序列上执行一次 AdamW 更新。
- 随后 greedy 生成 3 个 token，没有下载预训练权重。

### 实际训练输出

以下数值来自本次学习时粘贴的运行结果：

```text
输入：tensor([[1, 2, 3, 4]])
标签：tensor([[2, 3, 4, 5]])

logits 形状：torch.Size([1, 4, 10])
更新前的 loss：2.506772041320801
embedding 参数最大变化：0.010221719741821289
```

这说明输入标签正确对齐、输出形状符合预期，且至少部分 embedding 参数发生了更新。实验未打印更新后的损失，因此不能仅凭这些输出断言损失下降。

### 实际生成输出

| 轮次 | 当前输入 | 完整 logits | 最后位置 logits | 选出 ID | 追加后的序列 |
|---|---|---|---|---:|---|
| 1 | `[1,4]` | `[1,4,10]` | `[1,10]` | 5 | `[1,2,3,4,5]` |
| 2 | `[1,5]` | `[1,5,10]` | `[1,10]` | 6 | `[1,2,3,4,5,6]` |
| 3 | `[1,6]` | `[1,6,10]` | `[1,10]` | 9 | `[1,2,3,4,5,6,9]` |

表中“当前输入”一列记录形状。序列长度增长，词表维度始终为 10。

输出中出现 5、6 不足以说明模型学会了数数；本实验只验证训练与生成流程。脚本固定生成三次，未实现结束 token 检查，也不能直接生成超出位置表容量的长序列。

## 11. 学习记录

- [x] 理解残差相加的形状要求，以及零分支输出时保留 X。
- [x] 理解 LayerNorm 对每个 token 的特征维度归一化。
- [x] 理解 MLP 逐位置处理、Attention 跨位置汇总。
- [x] 理解完整 block 通常保持 `[B, T, d]` 形状。
- [x] 记录了 logits 形状，并澄清 logits 与概率的区别。
- [x] 理解 tokenizer ID 与输入 embedding、输出候选的对应关系。
- [x] 能构造向后错一位的训练标签。
- [x] 理解生成时使用最后位置输出，并将新 ID 追加到输入。
- [x] 理解普通生成不更新参数。
- [x] 运行小 GPT 的一次训练更新与三轮生成，获得符合预期的形状和输出。

本次学习记录到这里。后续笔记继续整理解码策略和 KV Cache。

## 参考材料

- [Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY)
- [配套 gpt.py](https://github.com/karpathy/ng-video-lecture/blob/master/gpt.py)
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
