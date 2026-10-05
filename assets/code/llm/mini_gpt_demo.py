import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(42)
torch.set_printoptions(precision=3, sci_mode=False)


class Block(nn.Module):
    def __init__(self, d=16):
        super().__init__()
        self.ln1 = nn.LayerNorm(d)
        self.attn = nn.MultiheadAttention(
            embed_dim=d, num_heads=2, batch_first=True
        )
        self.ln2 = nn.LayerNorm(d)
        self.mlp = nn.Sequential(
            nn.Linear(d, 4 * d),
            nn.ReLU(),
            nn.Linear(4 * d, d),
        )

    def forward(self, x):
        T = x.shape[1]

        # True 表示该位置需要屏蔽
        mask = torch.triu(
            torch.ones(T, T, dtype=torch.bool, device=x.device),
            diagonal=1,
        )

        h = self.ln1(x)
        a, _ = self.attn(
            h, h, h, attn_mask=mask, need_weights=False
        )
        x = x + a
        x = x + self.mlp(self.ln2(x))
        return x


class TinyGPT(nn.Module):
    def __init__(self, vocab_size=10, d=16, max_len=16):
        super().__init__()
        self.token_emb = nn.Embedding(vocab_size, d)
        self.position_emb = nn.Embedding(max_len, d)
        self.block = Block(d)
        self.final_ln = nn.LayerNorm(d)
        self.lm_head = nn.Linear(d, vocab_size)

    def forward(self, ids):
        T = ids.shape[1]
        positions = torch.arange(T, device=ids.device)

        x = self.token_emb(ids) + self.position_emb(positions)
        x = self.block(x)
        return self.lm_head(self.final_ln(x))


model = TinyGPT()

# 一、构造向后错一位的标签
sequence = torch.tensor([[1, 2, 3, 4, 5]])
inputs = sequence[:, :-1]
targets = sequence[:, 1:]

print("① 输入：", inputs)
print("   标签：", targets)

# 二、每个位置预测整个词表
logits = model(inputs)
print("\n② logits 形状：", logits.shape)

# 将 B、T 两个维度合并，每个位置成为一个预测样本
loss = F.cross_entropy(
    logits.reshape(-1, 10),
    targets.reshape(-1),
)
print("   更新前的 loss：", loss.item())

# 三、执行一次真正的参数更新
optimizer = torch.optim.AdamW(model.parameters(), lr=0.01)
before = model.token_emb.weight.detach().clone()

optimizer.zero_grad()
loss.backward()
optimizer.step()

change = (model.token_emb.weight.detach() - before).abs().max()
print("\n③ embedding 参数最大变化：", change.item())

# 四、生成：使用固定参数，每次追加一个 token
model.eval()
ids = inputs.clone()

with torch.no_grad():
    for step in range(10):
        logits = model(ids)
        last_logits = logits[:, -1, :]
        next_id = last_logits.argmax(dim=-1, keepdim=True)

        print(f"\n④ 生成第 {step + 1} 轮")
        print("   当前输入形状：", ids.shape)
        print("   logits 形状：", logits.shape)
        print("   最后位置 logits 形状：", last_logits.shape)
        print("   选出的 ID：", next_id.item())

        ids = torch.cat([ids, next_id], dim=1)
        print("   追加后的序列：", ids)