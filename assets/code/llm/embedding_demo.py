import torch
import torch.nn as nn

vocab_size = 10
embedding_dim = 4

embedding = nn.Embedding(vocab_size, embedding_dim)

ids = torch.tensor([2, 5, 7])

x = embedding(ids)

print(x)
print(x.shape)