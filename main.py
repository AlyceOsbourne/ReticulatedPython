from common_modules import *
import random
for epoch in range(1, 100):
    batch_size = 100
    print(f"Starting epoch {epoch} with a batch size of {batch_size}")
    train_tokenizer("tokens/Python_AST", batch_size)
