import math
import torch

torch.set_printoptions(precision=3, sci_mode=False)

# 三行分别代表：“我”“喜欢”“苹果”
# 教学用数值；真实模型中通过 X @ W_Q 等计算得到
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

# 1. 每个位置的 Query 与所有位置的 Key 匹配
d_k = Q.shape[-1]
scores = Q @ K.T / math.sqrt(d_k)

print("① 缩放后的分数，形状：", scores.shape)
print(scores)

# 2. 主对角线上方是未来位置，需要遮住
future_mask = torch.triu(
    torch.ones(3, 3, dtype=torch.bool),
    diagonal=1,
)
masked_scores = scores.masked_fill(future_mask, float("-inf"))

print("\n② 遮住未来位置后的分数：")
print(masked_scores)

# 3. 每一行独立归一化
weights = torch.softmax(masked_scores, dim=-1)

print("\n③ 注意力权重：")
print(weights)
print("每行之和：", weights.sum(dim=-1))

# 4. 按权重汇总 Value
output = weights @ V

print("\n④ Attention 输出，形状：", output.shape)
print(output)