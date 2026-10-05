---
title: "自回归大语言模型基础：表示、架构、训练与推理"
date: 2026-09-10 10:00:00 +0800
categories: [大模型]
tags: [LLM 基础]
description: >-
  自回归语言模型基础的综合笔记，覆盖表示、模型结构、训练和推理。
math: true
---

[返回大模型学习路线](/posts/llm-foundations/)

> 整理日期：2026-09-10
> 定位：LLM 最小知识集综合笔记；统一术语、符号与知识顺序，供复习和后续论文阅读使用。
> 范围：tokenization、embedding、Transformer、位置表示、预训练、SFT、RL、DPO、解码与 KV Cache。不展开前沿推荐论文、Semantic ID 或推荐评估。
> 学习依据：本站六步学习笔记、已完成的示例实验与后续图文复盘。公式采用便于教学的标准形式；具体模型实现可能不同。

## 摘要

自回归语言模型将文本编码为离散 token 序列，通过条件概率分解建模序列分布。Decoder-only Transformer 利用因果自注意力构造依赖前缀的表示，并通过输出投影预测下一个 token。预训练与监督微调通常采用 token 级交叉熵，但数据分布与损失覆盖范围不同；强化学习和直接偏好优化进一步引入奖励或偏好信号。推理时，解码策略决定如何从输出分数选择 token，KV Cache 与分组查询注意力则降低重复计算和缓存开销。理解上述层次的联系，是区分模型架构、训练目标和推理算法的基础。

## 1. 问题定义与统一符号

令文本经 tokenizer 编码后得到序列 x=(x₁,…,x_T)，每个 x_t 属于大小为 V 的离散词表。自回归语言模型对序列概率进行分解：

$$
p_\theta(x_{1:T})=\prod_{t=1}^{T}p_\theta(x_t\mid x_{<t}).
$$

首个 token 的预测可以以开始标记或给定前缀为条件。模型参数 θ 决定条件分布；解码算法在推理时利用这些分布产生序列。

| 符号 | 含义 |
|---|---|
| B | batch 大小 |
| T | 当前序列长度 |
| V | 词表大小 |
| d | 模型隐藏维度 |
| L | Transformer 层数 |
| H_Q、H_KV | Query head 数、Key/Value head 数 |
| d_k、d_v | 单头 Query/Key 维度、Value 维度 |
| E | token embedding 矩阵，形状为 V×d |
| Z | 输出 logits，形状为 B×T×V |
| τ | 采样温度，与序列长度 T 区分 |

全文省略部分偏置、Dropout 与 batch 维度以突出主干；标注形状时会明确上下文。

## 2. 离散表示：Tokenization

### 2.1 Token、ID 与词表

Tokenizer 将文本转换成 token ID 序列。Token 是离散编码单位，可能对应文本片段、字节片段或特殊标记；ID 是词表索引，其数值大小没有直接语义意义。

Token 边界不要求对应一个字、单词或词根。分词方案需要权衡词表大小、序列长度和覆盖能力。字符级序列往往较长；完整单词词表则难以覆盖新词和形态变化。

### 2.2 字节级 BPE

UTF-8 将 Unicode 文本编码为字节。完整的 256 种字节可作为基础单位，再通过 BPE（Byte Pair Encoding）合并常见相邻片段。

**训练 tokenizer：**统计相邻 token 对，按规则选择高频对，分配新 ID，替换后继续统计，直到达到目标词表规模或停止条件。输出包括词表与合并优先级。

**编码文本：**使用固定的预处理、预切分和已学习合并规则，将新文本转为 ID；不对每句话重新训练词表。

**解码序列：**将 ID 映射回字节片段，拼接后再进行文本解码。单个 token 可能只包含部分字符字节，不能要求每个 token 单独显示时都像完整文字。

```text
示例规则：h + u → hu；hu + g → hug
新输入： h u s h → hu s h
```

实际 tokenizer 可能先按正则规则预切分，限制 BPE 的合并边界。规范化、特殊 token 处理和字节回退机制因实现而异，并非所有 tokenizer 都是字节级 BPE。

### 2.3 与模型的接口约束

Tokenizer 的 ID 语义必须与模型输入 embedding 和输出词表对齐。两个 tokenizer 即使词表大小相同，也不能据此直接互换。

Tokenizer 训练与语言模型训练是不同过程：标准 BPE 使用统计与合并；语言模型通过反向传播学习参数。聊天模板和特殊标记组织角色与边界，但仍需由匹配的编码规则处理。

## 3. 连续表示：Embedding 与位置信息

### 3.1 Embedding lookup

$$
E\in\mathbb{R}^{V\times d},\qquad h_t^{(0)}=E[x_t].
$$

输入 ID 张量 B×T 查表后成为 B×T×d。E 是可学习参数，通常随语言模型训练更新。

同一参数状态下，相同 ID 的初始 token embedding 相同。位置处理和上下文计算之后，相同 token 在不同位置的隐藏表示可以不同。

### 3.2 可学习的绝对位置表示

一种简单方案为：

$$
h_t^{(0)}=E[x_t]+P[t],
$$

其中 P 为位置 embedding 表。这是小 GPT 实验采用的配置。位置表有容量限制，超出训练或实现支持的上下文长度需另行处理。

### 3.3 RoPE：旋转位置编码

标准 RoPE 根据位置对每个 head 的 Q、K 进行成对维度旋转，通常不旋转 V。设 R_t 为位置 t 的旋转变换：

$$
\widetilde q_i=R_iq_i,\quad \widetilde k_j=R_jk_j,
\qquad
\widetilde q_i^\top\widetilde k_j=q_i^\top R_{j-i}k_j.
$$

因此位置影响通过相对偏移进入点积分数。分数同时取决于内容向量，距离相同不保证分数相同。RoPE 不替代 causal mask，也不单独保证任意长度外推能力。

## 4. 因果自注意力

### 4.1 单头计算

对于单条序列 X∈R^(T×d)：

$$
Q=XW_Q,\quad K=XW_K,\quad V_h=XW_V,
$$

$$
A=\operatorname{softmax}_{\mathrm{row}}
\left(\frac{QK^\top}{\sqrt{d_k}}+M\right),
\qquad O=AV_h.
$$

这里 V_h 表示 Value 张量，避免与词表大小 V 混淆。

| 张量 | 形状 |
|---|---|
| Q、K | T×d_k |
| V_h | T×d_v |
| A | T×T |
| O | T×d_v |

A 的行对应查询位置，列对应被读取位置。Softmax 沿列维度逐行归一化：在无注意力 Dropout 时，每行权重之和为 1。训练中若在权重上施加 Dropout，单次采样后的行和不必严格为 1。

除以 √d_k 用于控制点积尺度。在分量具有适当方差的近似下，点积方差会随维度增长，缩放有助于避免 softmax 过度饱和。

### 4.2 因果约束

$$
M_{ij}=\begin{cases}0,&j\le i\\-\infty,&j>i.\end{cases}
$$

未来位置在 softmax 后获得零权重。第 i 个位置可访问 x₁,…,x_i，用于预测 x_(i+1)。这是并行训练时避免目标泄漏的关键。

### 4.3 Self-attention 与 Cross-attention

- Self-attention：Q/K/V 来自同一序列在当前层的表示。
- Cross-attention：Q 来自查询序列，K/V 来自另一序列，例如 decoder 读取 encoder 输出。

问题和回答拼接在同一 decoder-only 序列中时，回答读取问题仍属于 self-attention。文本角色与注意力来源是两个不同概念。

## 5. 多头结构与 Transformer Block

### 5.1 MHA、GQA、MQA

多头注意力用不同投影形成多个输出，沿特征维拼接后投影：

$$
\operatorname{MHA}(X)=\operatorname{Concat}(O_1,\ldots,O_H)W_O.
$$

| 结构 | Q head 与 KV head 的关系 |
|---|---|
| MHA | 每个 Q head 对应一组 KV |
| GQA | 多个 Q head 分组共享 KV |
| MQA | 全部 Q head 共享一组 KV |

共享 KV 不要求输出相同，不同 Q 可以产生不同权重。GQA 减少 KV 投影与缓存规模，但不等于同比减少整个模型计算或内存。

### 5.2 逐位置前馈网络

$$
\operatorname{FFN}(x)=\phi(xW_1+b_1)W_2+b_2.
$$

同一层各位置共享 FFN 参数，独立加工各自特征。Attention 直接混合位置间信息，FFN 进行位置内部非线性变换。小实验采用 d→4d→d 与 ReLU；现代模型可能采用其他激活或门控结构。

### 5.3 LayerNorm 与残差

$$
\operatorname{LN}(x)=\gamma\odot
\frac{x-\mu}{\sqrt{\sigma^2+\epsilon}}+\beta.
$$

均值与方差在每个位置的特征维计算，γ、β 为共享于各位置的可学习逐维参数。归一化不改变形状；仿射变换后的结果不必保持零均值、单位方差。

Pre-LN block 写为：

$$
Y=X+\operatorname{Attention}(\operatorname{LN}_1(X)),
\qquad
Z=Y+\operatorname{FFN}(\operatorname{LN}_2(Y)).
$$

残差为输入与梯度提供直接路径，子层可以学习调整量。整个 block 通常保持 B×T×d 形状。不同 block 通常拥有独立参数。Pre-LN 是具体配置，不能代表所有 Transformer。

## 6. Decoder-only 模型与输出分布

```text
IDs [B,T]
  → embedding 与位置处理 [B,T,d]
  → L 层 causal Transformer [B,T,d]
  → 最终归一化 [B,T,d]
  → LM head [B,T,V]
```

Decoder-only 直接基于因果前缀建模，没有必须存在的独立 encoder 或 encoder–decoder cross-attention。

输出投影为：

$$
z_t=h_tW_{\mathrm{out}}+b,\qquad
p_\theta(x_{t+1}=v\mid x_{\le t})=\operatorname{softmax}(z_t)_v.
$$

Logits 是未经归一化的实数分数，softmax 后才是概率。数学记法中 W_out 为 d×V；PyTorch Linear 的内部权重存储方向相反。

输入 embedding 与输出候选使用一致的 token ID 语义，但不一定共享参数。Weight tying 可将两者权重关联起来，本地小实验未使用。

## 7. 预训练与监督微调

### 7.1 自回归交叉熵

$$
\mathcal L_{\mathrm{CE}}=-\frac{1}{N}
\sum_{b,t}m_{b,t}\log p_\theta(x_{b,t+1}\mid x_{b,\le t}),
\qquad N=\sum_{b,t}m_{b,t}.
$$

m 表示有效预测目标是否计入损失。输入 `[1,2,3,4]` 对应标签 `[2,3,4,5]`。

训练时真实前缀已经给出，各位置的预测可并行计算；causal mask 阻止未来泄漏。这种利用真实前缀的方式通常称为 teacher forcing。

### 7.2 预训练

大规模文本本身提供后续 token 标签，属于自监督信号。模型通过预测学习语言与数据规律，但该目标没有单独规定统一的助手行为。

### 7.3 SFT

SFT 在已有模型上使用任务示范继续训练，常优化：

$$
\mathcal L_{\mathrm{SFT}}=-\mathbb E_{(x,y)\sim\mathcal D}
\left[\sum_{t\in\mathcal A}\log p_\theta(y_t\mid x,y_{<t})\right].
$$

x 为提示，y 为示范回答，A 为参与损失的回答位置；可进一步按 token 数归一化。常见方案仅计算回答损失，也有全序列损失配置。

Loss mask 决定哪些目标计入损失，attention mask 决定可读取哪些位置。问题不计直接预测损失，仍作为上下文，且回答损失可通过依赖问题的计算路径传播梯度。

### 7.4 训练目标与参数范围

全量微调和 LoRA 等参数高效方法决定更新哪些参数；SFT、RL 等决定训练目标。二者是独立选择。LoRA 通常冻结原权重，训练新增低秩参数，具体以配置为准。

## 8. 强化学习与偏好优化

### 8.1 奖励优化

LLM 的策略为条件 token 分布，状态为提示和前缀，动作为新 token。基本目标为：

$$
J(\theta)=\mathbb E_{x\sim\mathcal D,\,y\sim\pi_\theta(\cdot\mid x)}[r(x,y)].
$$

流程为生成回答、评价奖励、构造优化目标、更新参数。实际还常加入约束策略偏移的正则项等机制。

作为更新方向的示意，固定采样回答与优势估计 Â 后：

$$
\mathcal L_{\mathrm{PG}}=-\hat A\sum_t\log\pi_\theta(y_t\mid x,y_{<t}).
$$

正优势倾向提高该回答概率，负优势倾向降低。该式省略 PPO/GRPO 的概率比值、裁剪等细节，也不保证批量参数更新后每个样本概率严格按此方向变化。

无需对不可微的判题程序反向传播；奖励作为数值信号，梯度来自策略自身的 log 概率。

### 8.2 RLHF 与 RLVR

- 经典 RLHF：人类偏好对 → 训练奖励模型 → 为新生成回答评分 → RL 更新。
- RLVR：使用答案核对、代码测试等可验证奖励优化策略。

奖励是任务目标的近似。偏好分数不等于事实正确，有限测试不保证全面正确；奖励设计不当可能产生投机行为。

### 8.3 DPO

标准离线 DPO 使用 (x,y⁺,y⁻) 偏好对，并与固定参考策略比较。定义：

$$
\Delta_\theta=
\log\frac{\pi_\theta(y^+\mid x)}{\pi_{\mathrm{ref}}(y^+\mid x)}
-\log\frac{\pi_\theta(y^-\mid x)}{\pi_{\mathrm{ref}}(y^-\mid x)},
$$

$$
\mathcal L_{\mathrm{DPO}}=-\mathbb E[\log\sigma(\beta\Delta_\theta)].
$$

β>0 控制目标尺度，σ 是 sigmoid。该公式作为综合笔记的补充，不要求本阶段推导。

DPO 优化相对于参考策略的回答偏好，通常不另训显式奖励模型，也不要求标准离线流程持续在线采样。它不保证 chosen 绝对概率每次都提高，也不能与所有在线 RL 方法混称。

## 9. 自回归生成与解码

推理时取最后位置 logits，选择一个 token 并追加：

```text
当前 IDs [B,T] → logits [B,T,V]
              → 最后位置 [B,V]
              → 新 ID [B,1]
              → 追加后 [B,T+1]
```

普通生成固定参数。`eval()` 控制 Dropout 等模块行为，不自动关闭梯度；`no_grad()` 关闭梯度记录。实际还需结束标记和长度限制。

### 9.1 Greedy 与采样

Greedy 取 argmax，不需先做 softmax。Sampling 根据分布随机抽取候选。最高概率 token 最可能出现，但不保证每次选中。

### 9.2 温度与候选截断

$$
p_\tau(v)=\operatorname{softmax}(z/\tau)_v,\qquad\tau>0.
$$

低温使分布集中，高温使分布平缓；正温度不改变排序。温度不更新模型参数，τ=0 不能直接代入公式。

- Top-k：保留最高分的 k 个候选，归一化后抽一个。
- Top-p：按概率降序保留累计概率达到阈值的最小前缀集合，包括跨过阈值的候选，再归一化。

Top-k 固定数量，top-p 动态决定数量。组合使用时，温度、截断的处理顺序会影响最终分布，应查看实现。

### 9.3 Beam Search

维护多条前缀，每轮扩展后按累计分数筛选。原始序列分数为：

$$
\log p(y\mid x)=\sum_t\log p(y_t\mid x,y_{<t}).
$$

有限束宽可能提前淘汰最佳路径，不保证全局最优。不同长度常需长度惩罚或归一化；高模型概率也不必等于高任务质量。

Beam Search 搜索多条序列，top-k sampling 在一条前缀上筛选 token 并抽样，两者作用不同。

## 10. KV Cache 与推理效率

### 10.1 Prefill 与 Decode

Prefill 处理完整提示，计算并缓存各层 K/V，同时给出第一个新 token 的预测。随后 decode 每次处理新 token，读取旧缓存并追加新 K/V。

在固定参数、位置规则与正常因果推理下，旧位置不依赖后来追加的 token，故旧 K/V 可复用。RoPE 实现通常缓存旋转后的 K。

### 10.2 节省的计算

完整重算会再次计算旧位置各层的投影、Attention 输出和 FFN。缓存后只需处理新位置：

```text
无缓存的完整重算：Q [T,d_k] × Kᵀ [d_k,T] → [T,T]
缓存后的新位置：  Q [1,d_k] × Kᵀ [d_k,T] → [1,T]
```

旧 Query 通常无需保存，因为新位置使用自己的 Query。新 token 仍要读取历史 K/V，缓存没有消除历史注意力开销。

### 10.3 内存代价与 GQA

K/V 头维度均为 d_h 时，理想缓存存储量近似为：

$$
\text{bytes}_{KV}\approx2BLTH_{KV}d_hs,
$$

s 为每个元素的字节数，省略分配与管理开销。减少 H_KV 可降低缓存大小；序列变长、batch 增大也会增加缓存需求。

常规全序列训练保存激活用于反向传播，与跨生成步骤的 KV Cache 用途不同。

## 11. 已完成实验与证据边界

| 实验 | 已观察到的结果 | 不支持的扩大结论 |
|---|---|---|
| Tokenizer | 中文、英文编码与解码成功，切分不固定对应字词 | 所有 tokenizer 都逐字还原所有输入 |
| [Attention](/assets/code/llm/attention_demo.py) | mask 正确屏蔽未来；权重和输出形状符合预期 | 已训练出有语义的注意力 |
| [小 GPT](/assets/code/llm/mini_gpt_demo.py) | 错位标签、交叉熵、参数更新、逐步生成跑通 | 单步训练后学会数数或具备语言能力 |
| [解码](/assets/code/llm/decoding_demo.py) | 温度和候选截断改变分布，随机采样符合机制 | 20 次频率严格等于理论概率 |

小 GPT 更新前 loss 为 2.506772，embedding 最大变化约 0.010222；未记录更新后 loss，不能仅据此断言损失下降。生成 ID 为 5、6、9，不代表学会数列规则。

RoPE、GQA、SFT、RL、DPO 已做概念学习，尚未完成相应训练或实现实验。前沿推荐论文不在本笔记完成范围内。

## 12. 综合复习：区分四个层次

| 层次 | 回答的问题 | 代表内容 |
|---|---|---|
| 表示 | 文本如何进入模型？ | Tokenizer、ID、embedding、位置表示 |
| 架构 | 信息如何在模型内计算？ | Attention、FFN、残差、归一化 |
| 训练 | 模型如何学习，学习什么？ | 交叉熵、SFT、奖励、偏好优化 |
| 推理 | 如何产生输出并控制开销？ | 解码、KV Cache、缓存读取 |

最终主线是：文本离散化后，通过 embedding 与位置表示进入因果 Transformer；模型输出前缀条件下的候选分数；训练目标利用文本、示范、奖励或偏好更新参数；推理在固定参数下选择并追加 token，并通过缓存复用历史计算。

## 13. 分步笔记与延伸阅读

### 本地笔记

1. [Tokenization 与 Embedding](/posts/llm-tokenization-and-embedding/)
2. [Attention](/posts/llm-attention/)
3. [Transformer 与 Decoder-only](/posts/llm-transformer-and-decoder-only/)
4. [解码与 KV Cache](/posts/llm-decoding-and-kv-cache/)
5. [预训练、SFT、RL 与 DPO](/posts/llm-pretraining-sft-and-rl/)
6. [RoPE、GQA 与推荐衔接](/posts/llm-rope-gqa-and-generative-recommendation/)

### 原始材料入口

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Karpathy GPT 教学代码](https://github.com/karpathy/ng-video-lecture)
- [minbpe](https://github.com/karpathy/minbpe)
- [RoFormer / RoPE](https://arxiv.org/abs/2104.09864)
- [GQA](https://arxiv.org/abs/2305.13245)
- [InstructGPT](https://arxiv.org/abs/2203.02155)
- [DPO](https://arxiv.org/abs/2305.18290)
- [Hugging Face 解码教程](https://huggingface.co/blog/how-to-generate)

以上是概念溯源与后续阅读入口，不代表已完成对应论文精读或本轮在线核验。
