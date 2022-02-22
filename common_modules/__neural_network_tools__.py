from __future__ import annotations

import os

from tokenizers.implementations import SentencePieceBPETokenizer as Tokenizer

from common_modules.__data_collection import collect

tokenizer = Tokenizer(dropout=30)


def train(filename, batch_size=0):
    login = os.getenv("github_login")
    if not login:
        login = open("secret").read()
    tokenizer.train_from_iterator(collect(login, batch_size=batch_size), min_frequency=1000, vocab_size=20_000)
    print("Training Complete")
    print(tokenizer.to_str(pretty=True))
    tokenizer.save(filename, pretty=True)
