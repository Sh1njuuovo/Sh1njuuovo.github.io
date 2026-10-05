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
    print()