import re
from typing import Iterable, Union

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


class CodeLine:
    def __init__(self, text: str):
        self.text = text


class CodeBlockEnd:
    pass


MessageLine = Union[CodeLine, CodeBlockEnd]


def parse_message(message: str) -> Iterable[MessageLine]:
    in_code_block = False
    lines = message.splitlines()
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
                in_code_block = False
                yield CodeBlockEnd()
            else:
                yield CodeLine(line)
    if in_code_block:
        raise UnterminatedCodeBlock(lineno, line)


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
    code_blocks = []
    code_lines: list[str] = []
    for line in parse_message(message):
        if isinstance(line, CodeLine):
            code_lines.append(line.text.strip())
        elif isinstance(line, CodeBlockEnd):
            code_blocks.append(tuple(code_lines))
            code_lines.clear()
    if not code_blocks:
        raise NoCodeFound()
    return tuple(code_blocks)
