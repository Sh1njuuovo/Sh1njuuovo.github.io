---
title: "MixFormer：Dense 与行为序列的联合扩展"
date: 2026-09-11 23:30:00 +0800
categories: [论文, 推荐系统]
tags: ["Co-scaling", "序列建模"]
description: >-
  MixFormer 把特征交叉和行为序列聚合放进同一组重复 block，在固定算力预算下同时扩展 dense 容量和历史长度，并用单向 mask 让同一请求里的候选共享用户侧计算。
math: true
---

[全部论文](/categories/%E8%AE%BA%E6%96%87/)

- **论文**：MixFormer: Co-Scaling Up Dense and Sequence in Industrial Recommenders
- **作者**：Xu Huang、Hao Zhang、Zhifang Fan、Yunwen Huang 等，ByteDance
- **版本**：arXiv:2602.14110v2，2026-07-02，10 页，KDD 2026
- **链接**：[arXiv](https://arxiv.org/abs/2602.14110v2) · [DOI](https://doi.org/10.1145/3770855.3818447)

## 背景

工业推荐的精排阶段长期由两个模块分工：特征交叉负责非序列特征之间的高阶组合，序列建模负责从用户行为历史里提取兴趣。两者的组合方式主要有两类。串联式把序列建模的结果当成特征交叉的一部分输入，代表组合有 TA→DLRM、TA→DCNv2、STCA→RankMixer 等；并联式让两个模块各自算完再拼接，OneTrans 属于这一类。

这两类组合都把两个模块放在各自的参数空间里，因此在固定算力预算下会互相争抢：投给序列建模的计算多一点，特征交叉能分到的就少一点，反过来同样成立，很难在全局上找到最优的 scaling 设计。OneTrans 尝试用一个 Transformer 同时承担两件事，但 self-attention 直接作用在高度异构的特征上并不划算。不同特征字段来自不同的语义空间，用内积相似度算注意力权重很难建立起有意义的对齐，效果提升有限，计算开销却成倍增长。

## 整体思路

MixFormer 把两件事放进同一组重复 block：先让非序列特征互相交互形成 Query，再用这些 Query 去历史序列里取信息，最后融合成下一层的输入。特征交叉和序列建模因此共享同一条表示路径，可以一起扩展。

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

![图 1](/assets/img/mixformer/fig1-overview.png)

_图 1：MixFormer 整体架构。非序列特征先切分投影成 N 个 head，经过 L 层 MixFormer block 后接多个 TaskNet；每层由 Query Mixer、Cross Attention、Output Fusion 组成。_

这里有一点容易误读：论文说的“统一参数化”并不是所有 FFN 和投影共用一套权重。方法中每个 head、每一层的 FFN 与投影都是独立的，统一的是表示路径和 backbone。

## 方法

### 输入与切分

模型输入分为两类。序列特征是一段长度为 T 的历史行为 $S=[s_1,\dots,s_T]$，每个 $s_t$ 包含 item ID、action type、timestamp 和侧信息；非序列特征包含用户特征、候选物品特征和上下文特征。候选由上游提供，模型做的是候选条件化的多任务预测，预测 Finish 和 Skip 的 AUC 与 UAUC，这里的 decoder-style 表述不涉及自回归生成物品 ID。

非序列特征的 embedding 先拼成一个长度 $D_{ns}$ 的向量，再均匀切成 N 段，每段各自过一层线性映射得到 D 维表示：

$$
e_{ns}=[e_1;\dots;e_M],\quad d=D_{ns}/N,\quad
x_j=W_j\cdot e_{ns}[d(j-1):dj],\quad j=1,\dots,N.
$$

得到的 $X=[x_1,\dots,x_N]\in\mathbb R^{N\times D}$ 就是后面所有模块的主数据流，在 Cross Attention 里充当 Query。工程实现上可以把它看成 `[B, N, D]` 的张量，B 是 batch，N 是 head 数，D 是每个 head 的维度。相比把全部特征压成单头，切成多份能保留表征的多样性，让不同的特征语义落在不同的子空间里。

### Query Mixer

Query Mixer 负责非序列特征之间的高阶交互。既然在不同特征空间之间算注意力不可靠，这里就用一个没有参数的 mixing 操作（论文称 HeadMixing）代替 self-attention，再给每个 head 配一层独立的 SwiGLU FFN：

$$
P=[p_1,\dots,p_N]=\operatorname{HeadMixing}(\operatorname{Norm}(X))+X,
$$

$$
q_i=\operatorname{SwiGLUFFN}_i(\operatorname{Norm}(p_i))+p_i.
$$

HeadMixing 本身只是一次固定的 reshape 与 transpose，没有可训练权重，也没有相似度矩阵或 softmax，形状变化是 `[B,N,D] → [B,N,N,D/N] → 交换两个 N 轴 → [B,N,D]`。它的作用是让不同 head 的信息互相流动，代价主要在内存访问和布局转换上。后面每个 head 使用独立的 SwiGLU FFN，输出 $Q$ 仍然是 `[B,N,D]`。

### Cross Attention

Cross Attention 用 Query Mixer 的输出当作注意力的 Query，从历史序列里取信息。历史侧的处理是：每一层用本层自己的 SwiGLU FFN 把行为表示变换成 ND 维，再按 head 切开生成 K 和 V。

$$
h_t=\operatorname{SwiGLUFFN}^{(l)}(\operatorname{Norm}(s_t))+s_t\in\mathbb R^{ND},
$$

$$
h_t^i=h_t[iD:(i+1)D]\in\mathbb R^D,\quad
k_t^i=W_k^ih_t^i,\quad v_t^i=W_v^ih_t^i.
$$

Query Mixer 输出的 N 个 head 直接作为 N 个注意力头，每个头只关注历史序列的一个方面。把 softmax 的归一化轴写清楚，第 i 个头的输出是

$$
\alpha_{it}=\frac{\exp(q_i^Tk_t^i/\sqrt D)}{\sum_{r=1}^{T}\exp(q_i^Tk_r^i/\sqrt D)},\qquad
z_i=\sum_{t=1}^{T}\alpha_{it}v_t^i+q_i,
$$

也就是沿着历史长度 T 做归一化，再对 T 个位置的值加权求和。整个过程的张量变化是 `Q [B,N,D]`、`K/V [B,T,N,D]`，每个 head 对 T 个历史位置打分得到 `[B,N,T]`，最后加权求和并加上 Query 残差回到 `[B,N,D]`。式 5 里的上标 $(l)$ 表示层间参数独立；论文没有显式写出历史流在层间的递推形式，复现时这一点需要对着代码确认。

### Output Fusion

Cross Attention 的输出同时包含非序列特征的高阶信息和从历史里取回的信息，Output Fusion 负责把两者做一次深度非线性融合。由于各个 $z_i$ 捕捉的是不同 head 上的信息，属于异质的 token，这里同样给每个 head 独立的 FFN：

$$
o_i=\operatorname{SwiGLUFFN}_i(\operatorname{Norm}(z_i))+z_i.
$$

输出 $O$ 仍是 `[B,N,D]`，直接进入下一层。这样后一层的 Query Mixer 就能在已经融合过历史信息的基础上再做跨 head 交互。要注意这只是一个逐 head 的变换，真正跨 head 的交换发生在下一层的 Query Mixer 里，论文没有逐层语义的 probing 证据。

### 任务塔与训练配置

L 层堆叠之后接多个任务专属的 TaskNet，但论文没有披露具体 flatten / pooling 方式、head 层数和完整的多任务 loss 权重。训练配置上，batch 为 1500，dense 部分用 RMSProp、学习率 0.01，sparse 部分用 Adagrad；dense 参数同步更新，sparse 参数异步更新，训练在数百张 GPU 上分布式完成。论文给出的 medium 配置是 N=16、L=4、D=768。原文 small 配置写作 D=386，与图 1 中把 $D_{ns}$ 均匀拆成 N=16 份存在整除问题，可能是排版错误或有未披露的处理，复现前需要核实。

## 用户—物品解耦

线上精排的一个特点是：同一个用户请求会带上数百个候选物品，放在一个 batch 里打分。RLB（Request Level Batching）利用的就是这一点，把与候选无关的用户侧计算在整个请求内只算一次。原始 MixFormer 很难套用这个优化，因为非序列特征在 Query Mixer 里被充分混合之后，后续层里已经分不出哪些表示纯粹来自用户侧。

UI-MixFormer 把非序列特征显式拆成用户侧和物品侧两部分，分别占 $N_U$ 和 $N_G$ 个 head，两者之和为 N，实践中按 1:1 分配。随后在 HeadMixing 之后加一个单向 mask：user head 只能看到 user 侧的信息，item head 则可以同时看到两侧，于是 user head 始终与候选物品无关，可以跨候选复用。

![图 2](/assets/img/mixformer/fig2-ui-decoupled.png)

_图 2：解耦之后的架构。绿色是用户侧计算，同一请求内可以跨候选共享；红色是物品侧计算，每个候选都要单独算一遍。_

mask 的定义是（下标从 0 起）

$$
M_{ij}=\begin{cases}0,& i<N_U\ \text{and}\ j\ge N_U D/N,\\1,&\text{else},\end{cases}
\qquad
\operatorname{HM}_{\text{decouple}}(X)=M\odot\operatorname{HM}(X).
$$

实现上是先照常混合，再用 mask 抹掉从 item 侧流入 user head 的那部分信息。这条路径保留了 user→item 的影响，切断了 item→user 的路径，因此和完全双塔并不等价：user head 仍然参与和 item 的交互，只是它自己的计算不再依赖具体候选。需要留意的是，只有输入、归一化等环节都保持与候选无关时，共享才是安全的；论文把历史侧也列为可共享对象，但没有给出服务端缓存的实现细节，也没有与完全双塔做直接对照，因此不能认定两者效果与成本等价。

## 实验

### 离线效果与计算量

Table 1 的口径是：历史长度固定 512；参数量只统计 dense 参数，包含输入投影和 TaskNet 里的小模块，不含完整的 sparse embedding；计算量以 GFLOPs/Batch 计；训练 batch 为 1500，但原文没有说明这张表是否计入反向传播。还有一处需要在读表时记住：除了 UI 行，其他配置都没有开启 request-level batching，因此 UI-MixFormer 的下降是架构解耦和 RLB 两件事共同作用的结果，不是单纯的模型效率。

| 模型 | Finish AUC | Finish UAUC | Skip AUC | Skip UAUC | Dense M | GFLOPs/Batch |
|---|---|---|---|---|---|---|
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

除了基准那一行的绝对值，其余都是相对基线（TA→DLRM）的增益，按论文原始写法保留，没有换算成绝对 AUC。

对照最强的串联组合 STCA→RankMixer，MixFormer-medium 的 dense 参数更少（1226M 对 1255M），四项指标都更高，FLOPs 只有对方的 3503/6736≈52%。UI-MixFormer-medium 的指标与 medium 完全一致，FLOPs 进一步降到 2242，比 medium 低约 36%。不过这张表只给了单点的报告精度，指标相同并不能推出逐样本预测一致。

### 模块消融

Figure 3 对比的基准是 MixFormer-small，纵轴是 AUC Gain，图上直接标了数值：

| 改动 | AUC Gain |
|---|---|
| Query Mixer 去掉 HeadMixing | −0.03 |
| HeadMixing 换成 Self-Attention | +0.00 |
| Query Mixer 去掉 per-head FFN | −0.04 |
| Cross Attention 的 per-layer FFN 换成共享 | −0.03 |
| Output Fusion 的 per-head FFN 换成共享 | −0.06 |
| Pre-RMSNorm 换成 Post-LayerNorm | −0.01 |

![图 3](/assets/img/mixformer/fig3-ablation.png)

_图 3：模块消融，对比基准是 MixFormer-small，横轴是 AUC Gain。_

这组结果支持两点：跨 head 的交互和 per-head / per-layer 的独立参数都是有用的，其中 Output Fusion 的 per-head FFN 影响最大；在这个设置下把 HeadMixing 换成 self-attention 没有带来额外收益，也没有证据表明所有推荐任务都不适合 self-attention。最后一项同时改了 norm 的类型和位置，不能把变化只归因于其中一点。图中横轴沿用原文的 AUC Gain 单位，论文没有给换算定义，所以 −0.03 不能直接理解为绝对 AUC 下降 0.03。

### Co-scaling

Figure 4 和图 5 分别验证两条扩展轴，各自的固定条件不同：

| 实验 | 固定项 | 改变项 |
|---|---|---|
| Figure 4：Dense scaling | 历史长度固定 512 | 模块规模及 FLOPs |
| Figure 5：Sequence scaling | 各模型自身配置固定，起点选 FLOPs 相近的配置 | 序列长度 512 → 2048 → 8192 → 10000 |

![图 4](/assets/img/mixformer/fig4-dense-scaling.png)

_图 4：固定序列长度 512，只放大模块规模时的效果与计算量曲线。_

![图 5](/assets/img/mixformer/fig5-sequence-scaling.png)

_图 5：序列长度从 512 扩到 10000 时的效果曲线。_

图 4 里各组合基线按 1:1 分配 FLOPs，MixFormer 在图示预算范围内有更好的效果与计算量权衡。图 5 里 MixFormer 保持了较高的起点，并且随序列变长有和强序列模型接近的收益趋势。需要注意的是，图 5 只在起点让 FLOPs 尽量可比，序列加长之后各模型的 FLOPs 不再相等，也不能推定参数量严格相等，所以它支持的是“Dense 与 Sequence 都能受益”这个方向性结论，而不是任意预算下的普遍最优，更无法说明超过 10k 之后趋势是否延续。

### 推理时延

Figure 6 的横轴是候选规模，测试点大约落在 370 到 680 之间，各点精确的候选数没有单独列表。

| 图中点（从左至右） | MixFormer (ms) | UI-MixFormer (ms) | 图示 SpeedUp |
|---|---|---|---|
| 1 | 35.3 | 24.7 | 30.0% |
| 2 | 45.7 | 31.0 | 32.2% |
| 3 | 55.9 | 37.3 | 33.3% |
| 4 | 74.2 | 49.0 | 34.0% |

![图 6](/assets/img/mixformer/fig6-latency.png)

_图 6：不同候选规模下的服务时延与加速比。_

这里的百分比是 UI 版本延迟相对原版本的下降比例，也就是延迟下降约 30% 到 34%；换成比值，原延迟是 UI 版本的 1.43 到 1.51 倍。它不等于吞吐提升 34%，也不能直接推出生产环境的 QPS。这组数字成立的前提是 UI 解耦加 RLB 同时开启，硬件、batch 和负载控制等条件论文没有交代完整。

### 线上 A/B

Table 2 汇报了 Douyin 和 Douyin Lite 上连续两周的线上观察，对照模型是 STCA→RankMixer（超过 1B 参数）：

| Overall 指标 | Douyin | Douyin Lite |
|---|---|---|
| Active Days | +0.0415% | +0.0252% |
| Duration | +0.2799% | +0.4105% |
| Like | +0.1766% | +0.2125% |
| Finish | +0.3897% | +0.2924% |
| Comment | +0.7035% | +1.9097% |

原表还包含活跃度分组的细分结果。作者称收益统计显著且仍在增长，但论文没有给出流量、置信区间、p 值、方差和样本比例检查（SRM），外部无法独立复核这些增益。

## 小结

MixFormer 把特征交叉和序列建模收进同一组重复 block：Query Mixer 先做跨 head 交互，形成的每个 head 直接作为 cross-attention 的查询去读历史，再由 Output Fusion 逐 head 融合，输出接回下一层。这样两条能力共享一条表示路径，可以在同一份算力预算下一起放大。Table 1 显示它在参数更少的情况下优于最强的串联组合，Figure 4 和图 5 说明两条轴都还有继续扩展的空间。

更值得关注的是 UI-MixFormer。它在 HeadMixing 阶段就切断了 item→user 的信息流，让同一请求里数百个候选共享用户侧计算，Figure 6 测到约 30% 到 34% 的延迟下降，而指标与不做解耦的版本一致。和 HyFormer 相比，两者都在统一序列建模与特征交叉，MixFormer 的差异在于把服务侧的复用做进了模型结构里。

引用时需要注意几处边界：Table 1 的参数只统计 dense 部分，不能据此推断总存储；Figure 5 的 FLOPs 只在起点可比；线上收益缺少统计细节；UI 行的收益里混着 RLB 的作用。换到别的场景复现时，这几处都要重新验证。
