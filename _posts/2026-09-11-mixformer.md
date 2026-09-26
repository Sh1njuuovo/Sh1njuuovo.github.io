---
title: "MixFormer：Dense 与行为序列的联合扩展"
date: 2026-09-11 23:30:00 +0800
categories: [论文, 推荐系统]
tags: ["Co-scaling", "序列建模"]
description: >-
  MixFormer 把高阶特征交互和行为序列聚合放进同一组重复 block，在预算有限的前提下同时扩展 dense 容量和历史长度。
math: true
---
[全部论文](/categories/%E8%AE%BA%E6%96%87/)

> 整理日期：2026-09-11 · 方向：判别式推荐 / 联合建模 / Co-scaling / 服务复用
>
> 状态：已完成一轮辅助阅读；尚无完整独立复述、逐公式推导或代码实现证据。

| 资料 | 入口 |
|---|---|
| 论文 | *MixFormer: Co-Scaling Up Dense and Sequence in Industrial Recommenders* |
| 作者 | Xu Huang、Hao Zhang、Zhifang Fan、Yunwen Huang 等，ByteDance |
| 版本 | arXiv:2602.14110v2，2026-07-02，10 页；本地首页注明 KDD 2026 |
| 原文 | [arXiv v2](https://arxiv.org/abs/2602.14110v2) · [DOI](https://doi.org/10.1145/3770855.3818447) |
| 衔接 | RankMixer、HyFormer、行为序列基础，之后再补 |

**约定**：「论文内容」按本地 v2 核对；「教学例子」为自拟；「阅读判断」为证据解读；「整理补充」不代表本人已经掌握。PDF 页码按页序。图表读数只保留论文显示精度。

## 1. 一页速览

MixFormer 将高阶特征交互与行为聚合放入同一组重复 block：先形成 Query，再据此读历史，然后融合为下一层输入。其目标是在有限预算内同时利用更大 dense 容量和更长历史。

```text
非序列特征 → Embedding / Split
                  ↓
           Query Mixer：跨 head 交互
                  ↓
           Cross Attention ← 历史序列
                  ↓
           Output Fusion
                  ↓
           下一层 Block → TaskNets
```

| 核心问题 | 方法 | 主要证据 |
|---|---|---|
| 历史压缩与高阶特征交互割裂 | 每层 Query Mixer → Cross Attention → Output Fusion | Table 1 优于强串联和并联组合 |
| Dense 与 Sequence 争用计算预算 | 联合 backbone，分别检验模型与序列扩展 | Figure 4–5 |
| 同请求多候选重复计算用户侧 | UI-MixFormer 单向 mask + request-level batching（RLB） | Table 1 的 UI 行、Figure 6 时延 |

**阅读判断**：“统一参数化”不应理解为所有 FFN 和投影使用同一权重。方法明确包含 per-head、per-layer 独立参数；统一主要体现在共享表示路径和联合 backbone，不能凭措辞抹去这些独立模块。

## 2. 任务与数据

**论文内容（§3.1、§3.2、§4.1）**：工业排序、多任务行为预测。输入是用户、候选、上下文、交叉特征及历史；历史 action 包含 item ID、action type、timestamp 和侧信息。实验报告 Finish / Skip 的 AUC、UAUC。

候选由上游提供，模型进行候选条件化预测。这里的 decoder-style 表述不意味着自回归生成物品 ID。

数据为连续两周 Douyin 日志、万亿级 user-item 记录、每样本 300+ 特征。论文未完整披露负采样、候选构造、padding/truncation 和离线目标标注规则。§4.6 对线上 Finish 指标解释为完整播放次数，但不能由此补全离线 Finish/Skip 阈值定义。

**教学例子**：候选是 Transformer 教程，历史包含 Python、篮球、LLM、音乐、推荐系统视频；当前上下文为晚上、手机、WiFi。自拟 `P(Finish)=0.82, P(Skip)=0.06`。预测时刻之后的行为不能进入输入。

## 3. 输入、模块与张量形状

### 3.1 Embedding 与 Split

**论文内容（式 1–2）**：非序列 embedding 拼成长度 D_ns 的向量，均匀切成 N 段，各自投影到 D 维。

$$
e_{ns}=[e_1;\ldots;e_M],\quad d=D_{ns}/N,\quad
x_i=W_i e_{ns}[d(i-1):di].
$$

本笔记将结果写为 `[B,N,D]`，以区别于展平的 `[B,ND]`。N 是 feature/query head 数，D 是每 head 维度，T 是历史长度，L 是 block 数。

heads 不必分别对应固定的 user/item/context 语义。序列每个 action 在式 5 的残差接口为 ND 维；原始 embedding 如何对齐该接口未完整给出。

**教学配置**：N=4、D=8、T=5，非序列 X 为 `[B,4,8]`，对齐后的历史 S 为 `[B,5,32]`。D 可被 N 整除，能够走通 HeadMixing。

### 3.2 Query Mixer

**论文内容（§3.3.1，式 3–4）**：

$$
P=\operatorname{HeadMixing}(\operatorname{Norm}(X))+X,
$$

$$
q_i=\operatorname{SwiGLUFFN}_i(\operatorname{Norm}(p_i))+p_i.
$$

Figure 1 使用 RMSNorm，采用 Pre-Norm。HeadMixing 为固定 reshape / transpose：

```text
[B,N,D] → [B,N,N,D/N] → 交换两个 N 轴 → [B,N,D]
```

它没有可训练 mixing 权重、没有相似度矩阵或 softmax，但仍可能有内存访问和布局转换成本。之后每个 head 使用独立 SwiGLU FFN，输出 Q 仍为 `[B,N,D]`。

### 3.3 Cross Attention

**论文内容（§3.3.2，式 5–8）**：每层对历史 action 使用自己的 SwiGLU FFN，再按 head 切分生成 K/V。

$$
h_t=\operatorname{SwiGLUFFN}^{(l)}(\operatorname{Norm}(s_t))+s_t\in\mathbb R^{ND},
$$

$$
h_t^i\in\mathbb R^D,\quad k_t^i=W_k^ih_t^i,\quad v_t^i=W_v^ih_t^i.
$$

Query Mixer 的输出直接作为相应 attention head 的 Query。为了明确 softmax 的归一化轴，将式 8 写成：

$$
\alpha_{it}=\frac{\exp(q_i^Tk_t^i/\sqrt D)}{\sum_{r=1}^{T}\exp(q_i^Tk_r^i/\sqrt D)},\qquad
z_i=\sum_{t=1}^{T}\alpha_{it}v_t^i+q_i.
$$

```text
Q [B,N,D]，K/V [B,T,N,D]
→ 每 head 对 T 个历史位置打分：[B,N,T]
→ 历史加权和 + Query 残差：[B,N,D]
```

**整理补充**：per-layer FFN 表示层间参数独立；式 5 没有显式写 `s_t^(l-1)`，不能自行认定历史流采用标准递归 encoder。源码仍待核验。论文式 7 的 value 下标简写在这里统一为 v_t^i。

**修正后的教学数值**：对已缩放 logits `[1.4,-0.9,2.2,-0.4,2.0]`，softmax 约为：

```text
Python    篮球    LLM     音乐    推荐系统
0.1882   0.0189  0.4189  0.0311  0.3429
```

原稿 `[0.18,0.02,0.39,0.03,0.38]` 与该 logits 不对应；原稿保留，笔记按实际 softmax 更正。语义和数字均为教学自拟，不能视为真实 attention 可视化。

### 3.4 Output Fusion 与堆叠

**论文内容（§3.3.3，式 9）**：

$$
o_i=\operatorname{SwiGLUFFN}_i(\operatorname{Norm}(z_i))+z_i.
$$

O 为 `[B,N,D]`，进入下一层。因此后层 Query 可使用已融合的历史信息。Output Fusion 自身是 per-head 变换，下一层 Query Mixer 再做跨 head 交换。

“第一层找技术兴趣、第二层聚焦 Transformer”仅为解释，论文没有逐层语义 probing 证明此过程。

### 3.5 TaskNet、Loss、训练与推理

**论文内容**：L 层后接多个 task-specific networks。具体 flatten/pooling、head 层数、完整多任务 loss 和最终业务融合未披露，不能补成默认实现。

**教学例子**：BCE `−y log p−(1−y)log(1−p)`，正样本 p=0.82 时约 0.198。多任务加权和仅为教学闭环，各权重未确认。

训练配置（§4.1.4）：batch=1500，dense RMSProp、学习率 0.01，sparse Adagrad；dense 同步、sparse 异步更新，数百 GPU 分布式训练。推理固定参数，对候选前向预测，不需要标签或反向传播。

medium 配置为 N=16、L=4、D=768。**原文 small 配置写 D=386**，与图 1 均匀拆成 N=16 份存在整除疑问；可能涉及排版或未披露处理，不能擅自改成 384。复现前需核实。

## 4. UI-MixFormer：保留交互并共享用户侧计算

**论文内容（§3.4，图 2）**：将非序列 heads 分为用户侧 N_U 和物品侧 N_G，实践取 1:1。通过 HeadMixing 后的逐元素 mask 禁止 item 信息进入 user heads，保留 user → item 的影响。

式 10–11（按零起始下标）：

$$
M_{ij}=\begin{cases}0,&i<N_U\ \text{且}\ j\ge N_U D/N,\\1,&\text{其他},\end{cases}
\qquad
\operatorname{HM}_{decouple}(X)=M\odot\operatorname{HM}(X).
$$

**教学例子**：N=4、D=8、N_U=2；前两个输出 heads 的第 4–7 维屏蔽，后两个保留所有来源。切片位置依赖论文的 head 排序与重排布局。

同一请求中，candidate-independent 的用户表示、历史侧计算及用户 head 对历史的聚合可共享；item heads 仍逐候选计算。用户侧输入和归一化等也必须保持 candidate-independent，不能仅凭 mask 就推定所有实现都安全复用。

论文明确将历史侧列为可共享对象，但具体服务缓存代码未披露。完全双塔的效果/成本对比没有直接消融，不能认定两者等价。

## 5. Table 1：效果与计算量

**评估口径**：历史长度 512；参数仅为 dense 参数，包含输入投影及 TaskNet 小模块，不含完整 sparse embedding。原表 GFLOPs/Batch；训练 batch 为 1500，但原文未明确此表是否计入反向，不能借用 HyFormer 的 forward+backward 定义。

**重要表注**：除 UI-MixFormer 外，FLOPs 均未启用 request-level batching；UI 行使用该优化。因此 UI 的下降包含架构解耦与 RLB 联合作用。

| 模型 | Finish AUC | Finish UAUC | Skip AUC | Skip UAUC | Dense M | GFLOPs/Batch |
|---|---:|---:|---:|---:|---:|---:|
| TA → DLRM | 0.8554 | 0.8270 | 0.8124 | 0.7294 | 9 | 52 |
| TA → DCNv2 | +0.13% | +0.13% | +0.15% | +0.26% | 22 | 170 |
| TA → DHEN | +0.18% | +0.26% | +0.36% | +0.52% | 22 | 158 |
| TA → Wukong | +0.29% | +0.29% | +0.49% | +0.65% | 122 | 442 |
| STCA → DCNv2 | +0.89% | +0.91% | +1.05% | +1.65% | 145 | 4560 |
| TA → RankMixer | +0.95% | +1.22% | +1.25% | +1.82% | 1118 | 2180 |
| STCA → RankMixer | +1.12% | +1.40% | +1.43% | +2.14% | 1255 | 6736 |
| OneTrans（本文列为 Parallel） | +1.05% | +1.31% | +1.30% | +1.95% | 316 | 23371 |
| STCA ⊕ RankMixer | +1.11% | +1.38% | +1.42% | +2.11% | 1255 | 6736 |
| MixFormer-small | +1.01% | — | +1.18% | — | 282 | 733 |
| MixFormer-medium | +1.28% | +1.60% | +1.60% | +2.46% | 1226 | 3503 |
| UI-MixFormer-medium | +1.28% | +1.60% | +1.60% | +2.46% | 1226 | 2242 |

除基准绝对值外，保留论文原始 gain 写法；未核实换算公式，不自行还原绝对 AUC。模型分类是本文的组织方式，不代替对 OneTrans 原论文的独立判断。

**阅读判断与算术**：medium 比强串联基线参数略少，四项指标更高，FLOPs 为 `3503/6736≈52.00%`。UI 比 medium 的 FLOPs 低约 36.00%，四项指标在表中报告精度下相同，不能推定逐样本预测相同。

## 6. 消融与 Co-scaling

### 6.1 Figure 3：可直接读取的标签

**核对更正**：图中有明确数值标签，以下不是目测柱长估算。单位保留横轴原文 AUC Gain；未给换算定义，不解释成绝对 AUC 减少 0.03。

| 对 MixFormer-small 的改动 | 图示 AUC Gain |
|---|---:|
| Query Mixer 去掉 HeadMixing | −0.03 |
| HeadMixing 换成 Self-Attention | +0.00 |
| Query Mixer 去掉 per-head FFN | −0.04 |
| Cross Attention 的 per-layer FFN 换共享 | −0.03 |
| Output Fusion 的 per-head FFN 换共享 | −0.06 |
| Pre-RMSNorm 换 Post-LayerNorm | −0.01 |

这些支持跨 head 交互、per-head/per-layer 参数的作用；Self-Attention 在此设置未显示额外效果。FFN 共享改变容量；最后一项同时改变 norm 类型与位置，不能仅归因于其中之一。没有证据表明所有推荐任务都不适合 Self-Attention。

### 6.2 Figure 4–5：分别改变什么？

| 实验 | 固定项 / 选型条件 | 改变项 | 支持的结论 |
|---|---|---|---|
| 图 4 Dense scaling | 历史长 512 | 模块规模及 FLOPs | MixFormer 在图示预算内有更优效果–计算量权衡 |
| 图 5 Sequence scaling | 各模型配置固定；起点 512 时选择相近 FLOPs 的配置 | 512、2048、8192、10000 | MixFormer 保持较高起点，并有接近强序列模型的长度收益趋势 |

图 4 的组合基线按 1:1 FLOPs 分配。图 5 的 FLOPs 只在起点尽量可比，增加长度后不保证仍相同；也不能推定各模型参数严格相等。

“Dense 和 Sequence 都能受益”得到实验支持；没有证明任意数据、任意预算下普遍最优或超过 10k 后继续保持趋势。

## 7. 服务时延与线上收益

### 7.1 Figure 6：直接标注的时延

图中候选规模随横轴递增，约为 370–680；各点精确候选数未列成表，不把近似位置当作精确配置。

| 图中点（从左至右） | MixFormer ms | UI ms | 图示 SpeedUp |
|---|---:|---:|---:|
| 1 | 35.3 | 24.7 | 30.0% |
| 2 | 45.7 | 31.0 | 32.2% |
| 3 | 55.9 | 37.3 | 33.3% |
| 4 | 74.2 | 49.0 | 34.0% |

**整理补充**：这些百分比对应 `1−UI延迟/原延迟`，即延迟下降约 30%–34%；比值 `原延迟/UI延迟` 则约为 1.43–1.51 倍。不要将延迟下降 34% 与吞吐增加 34% 混为一谈，也不能由该测试直接推出生产 QPS。

结论限于 UI 解耦 + RLB 的测试条件；候选更多时共享用户计算更有价值，但具体硬件、batch 和负载控制仍不完整。

### 7.2 Table 2：两周在线观察

| Overall 指标 | Douyin | Douyin Lite |
|---|---:|---:|
| Active Days | +0.0415% | +0.0252% |
| Duration | +0.2799% | +0.4105% |
| Like | +0.1766% | +0.2125% |
| Finish | +0.3897% | +0.2924% |
| Comment | +0.7035% | +1.9097% |

对照线上 STCA → RankMixer（超过 1B 参数）。§4.6 明确报告 **两周** A/B 观察；原表还包含活跃度分组，见 PDF 第 7 页。作者称统计显著且收益仍在增长，但未完整报告流量、置信区间、p 值、方差及 SRM，不能独立复核。

## 8. 与已有两篇的联系

| 论文 | 本次阅读中的重点 |
|---|---|
| RankMixer | 以固定 Mixing + 独立 FFN 改善特征交互与硬件效率 |
| HyFormer | Decode 后 Boost，按序列保留 Query，并经 Split 进入下一层 |
| MixFormer | Mixer 形成的各 head 直接作为 cross-attention head，再经 Fusion；另设计 UI 单向复用 |

三者共享部分动机和组件；不能只凭模块先后顺序认定严格优劣、首创关系或完全等价。数据、指标、版本和 baseline 均不同，线上增益不能横向排名。

## 9. 成本和迁移边界

- Table 1 不含完整 sparse 参数，不能据 dense M 推断总存储。
- 未给完整 GPU-hours、收敛时长、训练 step、峰值内存等，不能证明总体训练费用更低。
- 单请求数百候选是 UI 复用收益的重要条件，逐条独立评估未必重现同等节省。
- 小数据可能首先受限于过拟合、短历史和稀少异质字段，不能直接复现十亿参数 / 10k 历史的趋势。
- 本次未核查最新代码发布或外部复现；不把“未查”写成“没有代码”。

## 10. 个人学习状态与待办

交接中本人主要通过提问和指定分析角度推进，没有完整机制复述或理解检查回答，也没有明确错误复述可记录。

| 内容 | 可确认状态 |
|---|---|
| 任务、数据流、三个模块、UI-MixFormer | 已辅助阅读，独立解释待验证 |
| Table 1、Figure 3–6、成本与证据边界 | 已讨论，独立评估待验证 |
| 逐公式推导与源码 | 未完成 |
| 项目计划 | 未讨论 |

### 下次优先自测

- [ ] 用 `[B,4,8]` 和 `[B,5,32]` 串起 Mixer、Attention、Fusion。
- [ ] 解释 Q 为什么直接对应 attention heads，softmax 沿哪一维归一化。
- [ ] 解释 mask 为什么允许 User → Item，以及有哪些用户侧计算可共享。
- [ ] 区分参数量、GFLOPs/Batch、延迟下降和加速倍数。
- [ ] 说明图 4–5 分别固定了什么，为什么仅起点 FLOPs 可比。

### 待核实

- [ ] small 的 D=386 与 N=16 的均匀分块如何兼容。
- [ ] 原始 action embedding 对齐 ND、历史流层间传递、K/V 投影共享规则。
- [ ] TaskNet 聚合、loss 权重、线上业务分数及样本标注细节。
- [ ] UI mask、归一化范围、head 布局和 RLB/cache 的实际代码。
- [ ] FLOPs 的前向/反向计数口径、完整训练成本和公平性控制。
- [ ] 完全双塔对照、逐层解释性、超过 10k 的趋势及公开数据适用性。

## 11. 整理核对记录

1. 本地 PDF 确认为 v2（2026-07-02），首页有 KDD 2026 与 DOI 信息。
2. 方法、设置与两张主表按 PDF 文本核对；第 7–8 页视觉核对图 3–6 和线上表。
3. 重算教学 softmax；图 3 更新为直接标注值，同时保留单位边界。
4. 标注 Table 1 UI 行启用 RLB 的例外，未混用 HyFormer 的训练 FLOPs 定义。
5. 区分延迟下降率与加速倍数，补充两周 A/B 观察。
6. 标注原文 small 的 D=386 整除疑问，不擅自修改原文配置。
7. 保留学习状态和未讨论的项目边界；原交接未改动。
