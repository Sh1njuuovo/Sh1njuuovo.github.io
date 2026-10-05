---
title: "LLM 基础：面向搜推论文的六步学习路线"
date: 2026-10-05 10:00:00 +0800
categories: [大模型]
tags: [LLM 基础]
description: >-
  面向搜推论文的六步大模型基础学习路线，附分步笔记和验收练习。
math: true
---

## 分步笔记

1. [Tokenization 与 Embedding](/posts/llm-tokenization-and-embedding/)
2. [Attention](/posts/llm-attention/)
3. [Transformer 与 Decoder-only LLM](/posts/llm-transformer-and-decoder-only/)
4. [解码策略与 KV Cache](/posts/llm-decoding-and-kv-cache/)
5. [预训练、SFT、RL 与 DPO](/posts/llm-pretraining-sft-and-rl/)
6. [RoPE、GQA 与生成式推荐](/posts/llm-rope-gqa-and-generative-recommendation/)

完成分步阅读后，可看[自回归大语言模型综合笔记](/posts/llm-integrated-notes/)复习。

> 创建：2026-09-08
> 目标：掌握 Transformer、Attention、decoder-only LLM、tokenization、SFT、RL、beam search，为阅读推荐论文和代码建立基础。
> 时间预算：5–6 天，约 14–18 小时；步骤 2、3 优先投入时间。

## 学习原则

- 以六步路线为主线，按需观看材料，达到验收要求就继续。
- CS336 作为查漏资料，暂不完整刷课或做作业。
- 小练习穿插进行，无需等待模型生成高质量文本。
- 每一步记录核心概念、一个例子和仍不理解的问题。
- 暂时跳过 MoE、分布式训练、FlashAttention 实现和 RL 算法完整推导。

## 1. Tokenization 与 Embedding｜约 2 小时

### 学习内容

- token、token ID、词表、embedding 的区别。
- Unicode、UTF-8 bytes 与 BPE 的基本关系。
- BPE 如何统计、合并，encode/decode 如何进行。
- 文本如何变成模型输入的向量序列。

### 材料

- [Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY)：开头的数据准备、字符编码和 embedding 部分。
- [Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE)：选看开头至 BPE 基础讲解完成，不必看完整视频。
- [minbpe](https://github.com/karpathy/minbpe)：作为代码备查，视频看懂后无需再完整学习一遍。

### 小练习与验收

- [ ] 对一段中文和英文观察 token、ID 与解码结果。
- [ ] 能解释：为什么 token 不一定对应一个字或一个单词？
- [ ] 能解释 token ID 如何变成 embedding。

## 2. Attention｜约 3 小时

### 学习内容

- Q、K、V 从哪里来，各自起什么作用。
- QKᵀ、缩放、softmax、乘以 V 的含义和形状。
- self-attention、cross-attention。
- causal mask 与 multi-head attention。

### 材料

- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)：重点看 Q/K/V、self-attention 和 multi-head 图解。
- [Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY)：从历史信息聚合到 self-attention、multi-head 的部分。
- [配套代码](https://github.com/karpathy/ng-video-lecture/blob/master/gpt.py)：看 `Head` 和 `MultiHeadAttention`。

### 小练习与验收

- [ ] 用三个 token 的例子，画出 attention 矩阵和 causal mask。
- [ ] 能逐项解释下方公式，并跟踪主要张量形状。
- [ ] 能解释多头与单头的区别，以及为什么不能读取未来位置。

$$
\operatorname{Attention}(Q,K,V)
=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V
$$

其中 M 为加性 mask：允许关注的位置为 0，需要屏蔽的位置为负无穷。

## 3. Transformer 与 Decoder-only LLM｜约 4 小时

### 学习内容

- Transformer block：Attention、MLP、残差、LayerNorm。
- 位置编码的作用。
- encoder、decoder、decoder-only 的基本区别。
- LM head、logits、next-token prediction。
- 输入与标签错位、交叉熵。
- 训练时并行计算各位置的预测，生成时逐 token 推进。

### 材料

- [Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY)：继续看完整 block、训练循环与生成。
- [配套代码](https://github.com/karpathy/ng-video-lecture/blob/master/gpt.py)：重点看 `get_batch`、`Block`、`forward`、`generate`。
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)：仅用于补整体结构、残差和归一化的直觉。

### 小练习与验收

- [ ] 为一句短文本写出训练输入与对应标签。
- [ ] 对照代码讲清楚：token ID → embedding → blocks → logits → loss／生成。
- [ ] 能解释训练时为什么不需要逐个生成输入 token。
- [ ] 有环境就跑一次小 GPT 的训练与生成，无需等待高质量输出。

## 4. 解码策略与 KV Cache｜约 2 小时

### 学习内容

- logits、softmax、temperature。
- greedy、sampling、top-k、top-p。
- beam search 的候选扩展、累计分数与结束条件。
- KV cache 缓存什么，为什么能降低重复计算。

### 材料

- [Hugging Face 生成策略教程](https://huggingface.co/blog/how-to-generate)：重点读上述解码策略。
- [CS336 讲义仓库](https://github.com/stanford-cs336/spring2025-lectures)：按 `KV cache` 查阅，理解动机即可。

### 小练习与验收

- [ ] 手算两步、beam width 为 2 的搜索。
- [ ] 用同一个提示词分别尝试 greedy、beam search 和 sampling；环境配置不顺时，先用概率表完成练习。
- [ ] 能区分序列搜索和随机采样，知道 beam search 不保证全局最优。
- [ ] 能说清 KV cache 缓存的是哪些中间结果。

## 5. 预训练、SFT 与 RL｜约 2–3 小时

### 学习内容

- 预训练：大量文本上的 next-token prediction。
- SFT：指令—回答示范、回答部分的损失。
- RL：采样回答、获得奖励、根据奖励更新模型。
- 人类偏好奖励与可验证奖励。
- DPO 只做概念补充：了解偏好对数据，以及它与在线采样的 RL 训练流程不同。

### 材料

- [Deep Dive into LLMs like ChatGPT](https://www.youtube.com/watch?v=7xTGNNLPyMI)：选看预训练、SFT、RL 相关章节。
- [Hugging Face TRL](https://github.com/huggingface/trl)：仅用于查看 SFT、DPO、奖励优化等方法的定位，暂不学习训练 API。

### 小练习与验收

- [ ] 用同一个问答任务，分别举出预训练文本、SFT 样本、偏好对和奖励信号。
- [ ] 能解释各阶段用什么数据、优化什么目标。
- 暂时跳过 PPO、GRPO 推导，以及完整微调实验。

## 6. 补充现代 LLM 概念，衔接推荐｜约 1–2 小时

### 学习内容

- RoPE：位置信息如何影响 Q/K 与注意力分数。
- GQA：共享部分 K/V 如何减少缓存开销。
- 文本 token 与 item／Semantic ID 的对应关系。
- next-token prediction 与 next-item prediction。
- 合法物品约束与 constrained decoding 的动机。

### 材料

- [RoPE](https://arxiv.org/abs/2104.09864)：摘要、引言与方法直觉。
- [GQA](https://arxiv.org/abs/2305.13245)：MHA、MQA、GQA 的结构对比图。
- [TIGER](https://arxiv.org/abs/2305.05065)：摘要、整体框架图、物品表示与生成流程，作为下一阶段预习。

### 小练习与验收

- [ ] 解释一件物品如何表示为一个或多个 token。
- [ ] 解释为什么生成的 token 序列需要映射回合法物品。
- [ ] 理解这种对应关系只是入口，推荐还涉及物品表示、候选空间、用户反馈和评价指标。

## 建议执行节奏

| 时间 | 内容 |
|---|---|
| 第 1 天 | 步骤 1：Tokenization 与 Embedding |
| 第 2 天 | 步骤 2：Attention |
| 第 3–4 天 | 步骤 3–4：Transformer、训练生成流程、解码策略 |
| 第 5 天 | 步骤 5：预训练、SFT 与 RL |
| 第 6 天 | 步骤 6：衔接推荐，并查漏 |

步骤 1–5 掌握后即可进入推荐论文；步骤 6 可以随论文阅读补齐。时间预算包含暂停理解与小练习，不以视频播放时长代替学习时长。
