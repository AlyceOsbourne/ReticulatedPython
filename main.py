from common_modules import *

for epoch in range(1, 10_000):
    batch_size = 100
    print(f"Starting epoch {epoch} with a batch size of {batch_size}")
    train_tokenizer("tokens/Python_AST", batch_size)
