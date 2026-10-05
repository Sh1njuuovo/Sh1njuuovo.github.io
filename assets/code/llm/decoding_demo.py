import torch

torch.set_printoptions(precision=3, sci_mode=False)
torch.manual_seed(42)

tokens = ["苹果", "音乐", "电影", "游戏"]
logits = torch.tensor([3.0, 2.0, 1.0, 0.0])


def show(name, scores):
    probs = torch.softmax(scores, dim=-1)
    print(f"\n{name}")
    for token, prob in zip(tokens, probs.tolist()):
        print(f"  {token}：{prob:.3f}")
    return probs


# 1. Greedy：直接选最高分
print("Greedy：", tokens[logits.argmax().item()])


# 2. Temperature：改变概率分布的集中程度
for temperature in [0.5, 1.0, 2.0]:
    show(
        f"Temperature = {temperature}",
        logits / temperature,
    )


# 3. Top-k：保留最高分的 k 个候选
k = 2
_, indices = torch.topk(logits, k)

top_k_logits = torch.full_like(logits, float("-inf"))
top_k_logits[indices] = logits[indices]
show("Top-k = 2", top_k_logits)


# 4. Top-p：按概率排序，保留累计概率达到 p 的最小集合
p = 0.9
sorted_logits, sorted_indices = torch.sort(
    logits, descending=True
)
sorted_probs = torch.softmax(sorted_logits, dim=-1)
cumulative = torch.cumsum(sorted_probs, dim=-1)

# 当前 token 之前的累计概率 < p 时，保留当前 token。
# 这样会保留使累计概率首次达到或超过 p 的那个 token。
cumulative_before = torch.cat([
    torch.zeros_like(cumulative[:1]),
    cumulative[:-1],
])
keep = cumulative_before < p

top_p_logits = torch.full_like(logits, float("-inf"))
kept_indices = sorted_indices[keep]
top_p_logits[kept_indices] = logits[kept_indices]

show("Top-p = 0.9", top_p_logits)


# 5. Sampling：从原始概率分布中独立抽取 20 次
probs = torch.softmax(logits, dim=-1)
sampled_ids = torch.multinomial(
    probs, num_samples=20, replacement=True
)
print("\n原始分布独立采样 20 次：")
print([tokens[i] for i in sampled_ids.tolist()])