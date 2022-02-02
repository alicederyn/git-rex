import re

CODE_BLOCK = re.compile(r"\s*```(\w*)\s*$")


class NoCodeFound(Exception):
    pass


class UnsupportedCodeSyntax(Exception):
    def __init__(self, lineno: int):
        self.lineno = lineno


class UnexpectedCodeBlock(Exception):
    def __init__(self, lineno: int):
        self.lineno = lineno


class UnterminatedCodeBlock(Exception):
    pass


def extract_scripts(message: str) -> tuple[tuple[str, ...], ...]:
    """Extracts code from between triple-tick blocks

    >>> commit_message = '''Sample commit
    ...
    ... This commit did some stuff
    ...
    ... ```bash
    ... run_my_code thing
    ... and_my_other thing
    ... ```
    ...
    ... ```bash
    ... run_a_third thing
    ... ```
    ... '''
    >>> extract_scripts(commit_message)
    (('run_my_code thing', 'and_my_other thing'), ('run_a_third thing',))
    """
    in_code_block = False
    lines = message.splitlines()
    code_blocks = []
    code_lines: list[str] = []
    for lineno, line in enumerate(lines, start=1):
        if not in_code_block:
            if m := CODE_BLOCK.match(line):
                if m.group(1) != "bash":
                    raise UnsupportedCodeSyntax(lineno)
                in_code_block = True
        else:
            if m := CODE_BLOCK.match(line):
                if m.group(1):
                    raise UnexpectedCodeBlock(lineno)
                code_blocks.append(tuple(code_lines))
                code_lines.clear()
                in_code_block = False
            elif line.strip():
                code_lines.append(line.strip())
    if in_code_block:
        raise UnterminatedCodeBlock()
    if not code_blocks:
        raise NoCodeFound()
    return tuple(code_blocks)
