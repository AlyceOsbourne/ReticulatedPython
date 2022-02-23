from __future__ import annotations

import ast
import os

import astor
from tokenizers.implementations import ByteLevelBPETokenizer as Tokenizer

from common_modules.__data_collection import collect

tokenizer = Tokenizer("tokens/Python_AST-vocab.json", "tokens/Python_AST-merges.txt")


def data_to_ast(iterator):
    for _file in iterator:
        try:
            # yielding the "pretty" dump, so we can split on \n to tokenize into statements
            yield astor.dump_tree(ast.parse(_file))
        except (SyntaxError, ValueError, AttributeError) as e:
            print(
                f"file failed to parse to ast with error: {e.__class__.__name__}, "
                f"suggests bad data, discarding and moving on")
            continue


def split_lines(iterator):
    for _file in iterator:
        print("       Splitting file")
        lines = _file.split("\n")
        print(f"        File split into {len(lines)} lines\n")
        for line in lines:
            yield line.strip()


def process_github(login, batch_size):
    for i in split_lines(data_to_ast(collect(login, batch_size=batch_size))):
        yield i


def train_tokenizer(filename, batch_size=0):
    login = os.getenv("github_login")
    if not login:
        login = open("secret").read()
    login = {"login_or_token": login}
    tokenizer.train_from_iterator(process_github(login, batch_size), min_frequency=1000,
                                  vocab_size=20_000, show_progress=False)
    print("Training Complete")
    print(tokenizer.to_str(pretty=True))
    tokenizer.save_model(".", filename)
