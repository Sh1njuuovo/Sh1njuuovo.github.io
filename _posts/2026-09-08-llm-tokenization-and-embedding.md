---
title: "1 Tokenization 与 Embedding 笔记"
date: 2026-10-05 10:07:00 +0800
categories: [大模型]
tags: [LLM 基础]
description: >-
  从 token、BPE 和词表到 embedding，记录文本进入模型的过程与实验。
math: true
---

[返回大模型学习路线](/posts/llm-foundations/)

> 整理日期：2026-09-08
> 所属路线：[LLM 基础六步学习路线](/posts/llm-foundations/)
> 状态：已运行 tokenizer 实验，并记录 BPE 合并与 embedding 查表的例子。

## 1. 这一节的主线

```text
原始文本
  ↓ tokenizer：切分并编号
token ID 序列
  ↓ embedding lookup：按 ID 查表
向量序列
  ↓ 后续位置处理与 Transformer
结合上下文的表示
```

| 概念 | 含义 |
|---|---|
| token | 分词器使用的离散单位，可以对应文本片段或字节片段，也可以是特殊标记 |
| vocabulary（词表） | 分词器支持的 token 及其 ID 的对应关系 |
| token ID | token 的整数编号，本身不代表语义大小或距离 |
| tokenizer | 将文本编码为 ID 序列、将 ID 序列解码为文本的程序与规则 |
| embedding | 模型中与 token ID 对应的可学习向量 |

tokenizer 负责离散化，embedding 层负责把离散编号转换为连续向量。

## 2. Token 为什么不一定是一个字或一个单词

切分需要兼顾词表大小和序列长度：

- 按字符切分，序列通常较长；固定字符词表也可能遇到未覆盖字符。
- 按完整单词切分，词表容易变大，新词、拼写变化和代码等也难以覆盖。
- 子词或字节级方案可以复用片段，用多个 token 表示罕见文本。

因此，一个词可能被拆成多个 token，多个汉字也可能合成一个 token。切分边界不要求符合语法、词根或语义边界。

### Unicode、UTF-8 与字节

- Unicode 为码点分配编号，例如 `A` 是 `U+0041`。
- UTF-8 将 Unicode 码点编码为字节；一个 Unicode 标量值需要 1–4 个字节。
- `A` 的 UTF-8 编码占 1 个字节，`中` 占 3 个字节。
- 用户看到的一个字符有时由多个码点组成，例如部分 emoji。

对于字节级 BPE，可以把流程理解为：文本 → UTF-8 字节 → 按合并规则组成 token → ID。并非所有 tokenizer 都使用完全相同的流程。

## 3. 真实 tokenizer 实验

使用 `Qwen/Qwen3-0.6B` 的 tokenizer，未加载语言模型权重。

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")

texts = [
    "我喜欢机器学习",
    "I love machine learning",
    "unbelievable",
]

for text in texts:
    ids = tokenizer.encode(text, add_special_tokens=False)
    tokens = tokenizer.convert_ids_to_tokens(ids)
    restored = tokenizer.decode(ids, clean_up_tokenization_spaces=False)

    print("原文：", text)
    print("Token 数量：", len(ids))
    print("Token IDs：", ids)
    print("Tokens：", tokens)
    print("解码结果：", restored)
    print("是否还原：", restored == text)
```

### 本次实际运行结果

以下记录来自学习时粘贴的运行输出，具体 ID 属于本次使用的 tokenizer。

| 原文 | Token 数 | Token IDs | 切分的可读表示 |
|---|---:|---|---|
| 我喜欢机器学习 | 3 | `[109366, 102182, 100134]` | `我喜欢` / `机器` / `学习` |
| I love machine learning | 4 | `[40, 2948, 5662, 6832]` | `I` / ` love` / ` machine` / ` learning` |
| unbelievable | 3 | `[359, 31798, 23760]` | `un` / `belie` / `vable` |

三个输入的 `restored == text` 都是 `True`。

英文内部 token 表示为：

```text
['I', 'Ġlove', 'Ġmachine', 'Ġlearning']
```

这里的 `Ġ` 表示该 token 包含前面的空格。中文内部表示看起来像乱码，是字节到可显示字符的映射方式，不代表解码失败。单个 token 也可能只包含一个汉字的部分字节，因此查看完整序列的解码结果更可靠。

### 从结果得到的结论

1. 7 个汉字可以对应 3 个 token。
2. 空格可以与后面的文本合在一个 token 中。
3. `unbelievable` 被切为 `un / belie / vable`，没有严格按词缀切分。
4. 这三段文本成功往返还原；其他 tokenizer 可能包含规范化操作，不能将此推广为所有输入、所有分词器都逐字还原。

运行时提示未安装 PyTorch，没有阻止本次 tokenizer 实验。未认证的下载提示也未阻止文件下载。

## 4. 手动理解 BPE

BPE 的核心是反复统计相邻单位，把高频组合合并为新 token。下面使用简化的字符级例子，规定不跨词合并。

训练语料中 `hug` 出现两次，`hugs` 出现一次：

```text
h u g
h u g
h u g s
```

### 第一轮

| 相邻组合 | 次数 |
|---|---:|
| `h + u` | 3 |
| `u + g` | 3 |
| `g + s` | 1 |

前两项并列，这个例子约定先选 `h + u → hu`。合并后：

```text
hu g
hu g
hu g s
```

词表新增 `hu`，基础单位 `h`、`u` 仍然保留。

### 第二轮

重新统计后，`hu + g` 出现 3 次，`g + s` 出现 1 次。选择 `hu + g → hug`：

```text
hug
hug
hug s
```

假设此时停止训练，得到有顺序的两条合并规则：

```text
1. h + u  → hu
2. hu + g → hug
```

### 编码新文本：hush

```text
h u s h
  ↓ 应用第一条规则
hu s h
```

`hu` 后面没有 `g`，第二条规则无法应用。最终是 `[hu, s, h]`，共 3 个 token。

**训练 tokenizer 时学习词表与合并规则；编码新文本时使用已学好的规则，不为每句话重新训练 tokenizer。**

## 5. Token ID 如何变成 Embedding

设词表大小为 V，每个向量的维度为 d，embedding 矩阵为：

$$
E \in \mathbb{R}^{V \times d}
$$

每个 ID 对应一行，查表可以理解为 `E[token_id]`。ID 大小不代表语义强弱，ID 接近也不代表语义接近。

### 查表例子

下面全部是简化的数字：

| ID | Token | 向量 |
|---:|---|---|
| 0 | 我 | `[0.1, 0.2, 0.3]` |
| 1 | 喜欢 | `[0.4, 0.5, 0.6]` |
| 2 | 猫 | `[0.7, 0.8, 0.9]` |
| 3 | 狗 | `[1.0, 1.1, 1.2]` |

这里 V=4、d=3。输入 `[0, 1, 2]` 查表后得到：

```text
[
  [0.1, 0.2, 0.3],
  [0.4, 0.5, 0.6],
  [0.7, 0.8, 0.9]
]
```

输出形状为 `[3, 3]`：3 个 token，每个对应 3 维向量。

一般来说，长度为 T 的 ID 序列查表后得到 `[T, d]`；若包含 B 条等长序列，则从 `[B, T]` 变为 `[B, T, d]`。

### 同一个 token 的向量是否相同

在同一份模型参数下，刚完成查表、尚未进行位置处理或 Transformer 计算时，同一个 ID 总是取到同一行。

因此 `猫 喜欢 猫` 中两个“猫”的初始 token embedding 相同。后续结合位置与上下文后，两处表示可以不同。

### 训练时更新什么

通常保持 token ID 不变，通过反向传播和优化器更新 embedding 矩阵里的浮点参数。例如 ID 2 仍然代表“猫”，其向量数值可以发生变化。

embedding 通常从随机初始化开始，在模型训练中学习对任务有用的结构；不能把随机初始化的向量当作已有语义的表示。

## 6. 与推荐系统的联系

| LLM | 推荐系统中的对应概念 |
|---|---|
| token ID | item ID |
| token 词表 | 物品集合 |
| token embedding | item embedding |
| token 序列 | 用户行为序列 |

例如 `iPhone → AirPods → MacBook` 可以先映射成 item ID 序列，再查表得到向量序列。这里对应的是 ID 查表机制；Semantic ID 的构造等内容留到生成式推荐阶段。

## 7. 学习记录

- [x] 实际运行中文、英文的 encode/decode，观察切分并成功还原。
- [x] 理解 token 不固定对应一个字或一个单词。
- [x] 按两条已学到的 BPE 规则将 `hush` 编码成 `[hu, s, h]`。
- [x] 理解 token ID 是编号，embedding 是可学习向量。
- [x] 独立回答：3 个 ID 在 `[100, 16]` 的 embedding 矩阵中查表，输出是 `[3, 16]`。
- [x] 独立回答：100 是词表大小，16 是向量维度；同一个 token 刚查表时向量相同。
- [ ] 待补充：独立运行一次 PyTorch `nn.Embedding` 实验；尚未确认完成，留待后续复习。

本次学习记录到这里。后续阅读 Attention 时，重点看每个位置如何结合其他位置的信息。

## 参考材料

- [Karpathy：Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE)
- [minbpe](https://github.com/karpathy/minbpe)
- [Let's build GPT 配套代码](https://github.com/karpathy/ng-video-lecture)

材料用于按需查漏，无需全部看完后才进入下一步。
