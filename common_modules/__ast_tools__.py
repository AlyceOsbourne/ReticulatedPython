import ast

import astor


def to_string(node):
    return astor.dump_tree(node)


def from_string(string):
    return ast.parse(string)


def to_source(node):
    return astor.to_source(node)


def restructurize(file):
    if not file.endswith(".py"):
        return

    with open(file, 'r') as py_in, open(file.replace(".py", "_restructured.py"), 'w') as py_out:
        break_lines = "\n" * 3, "#" * 100, "\n" * 2
        try:
            print(file, *break_lines)
            input_code = py_in.read()
            print(input_code, *break_lines)
            parsed_ast = ast.parse(input_code)
            ast_string = astor.dump_tree(parsed_ast)
            print(ast_string, *break_lines)
            recompiled_source = astor.to_source(parsed_ast)
            print(recompiled_source, *break_lines)
            py_out.write(recompiled_source)

        except Exception:
            print("Failed to create file")
            exit(-1)
