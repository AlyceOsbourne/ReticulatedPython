from __future__ import annotations
from tokenizers.implementations import ByteLevelBPETokenizer
import secret
from data_collection import collect

tokenizer = ByteLevelBPETokenizer(dropout=100)
tokenizer.train_from_iterator(collect(secret.github_login, batch_size=1000), min_frequency=1000, vocab_size=20_000)
tokenizer.save("test", pretty=True)

print(tokenizer.to_str(True))