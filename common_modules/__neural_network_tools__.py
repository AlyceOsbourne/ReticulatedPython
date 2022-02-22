from __future__ import annotations
import os
from tokenizers.implementations import ByteLevelBPETokenizer
from data_collection import collect
login = os.getenv("github_login", default=str(open("secret").read()))
tokenizer = ByteLevelBPETokenizer(dropout=100)
tokenizer.train_from_iterator(collect(login, batch_size=1000), min_frequency=1000, vocab_size=20_000)
tokenizer.save("test", pretty=True)

#print(tokenizer.to_str(True))