from __future__ import annotations
import os
from tokenizers.implementations import ByteLevelBPETokenizer
from common_modules.data_collection import collect

tokenizer = ByteLevelBPETokenizer(dropout=100)
def train(batch_size):
	login = os.getenv("github_login")
	if not login:
	    login = open("secret").read()
		tokenizer.train_from_iterator(collect(login, batch_size=batch_size), min_frequency=1000, vocab_size=20_000)
	print("Training Complete")
	tokenizer.save("python_tokens", pretty=True)

