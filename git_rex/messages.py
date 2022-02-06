import re
from typing import Iterable, List, Tuple, Union

from .bash import BashScript

CODE_BLOCK = re.compile(r"\s*```(\w*)\s*$")


class NoScriptBlockFound(Exception):
    pass


class NoExecutableCodeFound(Exception):
    pass


class UnsupportedCodeSyntax(Exception):
    def __init__(self, lineno: int):
        self.lineno = lineno


class UnexpectedCodeBlock(Exception):
    def __init__(self, lineno: int):
        self.lineno = lineno


class UnterminatedCodeBlock(Exception):
    pass


class TextLine:
    def __init__(self, text: str):
        self.text = text


class CodeBlockStart:
    def __init__(self, text: str, lineno: int):
        self.text = text
        self.lineno = lineno


class CodeLine:
    def __init__(self, text: str):
        self.text = text


class CodeBlockEnd:
    def __init__(self, text: str):
        self.text = text


MessageLine = Union[TextLine, CodeBlockStart, CodeLine, CodeBlockEnd]


def parse_message(message: str) -> Iterable[MessageLine]:
    in_code_block = False
    lines = message.splitlines()
    for lineno, line in enumerate(lines, start=1):
        if not in_code_block:
            if m := CODE_BLOCK.match(line):
                if m.group(1) != "bash":
                    raise UnsupportedCodeSyntax(lineno)
                yield CodeBlockStart(line, lineno)
                in_code_block = True
            else:
                yield TextLine(line)
        else:
            if m := CODE_BLOCK.match(line):
                if m.group(1):
                    raise UnexpectedCodeBlock(lineno)
                in_code_block = False
                yield CodeBlockEnd(line)
            else:
                yield CodeLine(line)
    if in_code_block:
        raise UnterminatedCodeBlock(lineno, line)


def extract_scripts(message: str) -> Tuple[BashScript, ...]:
    """Extracts code from between triple-tick blocks

    >>> commit_message = '''Sample commit
    ...
    ... This commit did some stuff
    ...
    ... ```bash
    ... do_a thing
    ... and_a thing
    ... ```
    ...
    ... ```bash
    ... do stuff
    ... ```
    ... '''
    >>> scripts = extract_scripts(commit_message)
    >>> print(scripts[0])
    6: do_a thing
    7: and_a thing
    >>> print(scripts[1])
    11: do stuff
    """
    code_blocks = []
    code_lines: List[str] = []
    first_lineno: int = 0
    for line in parse_message(message):
        if isinstance(line, CodeBlockStart):
            first_lineno = line.lineno + 1
        elif isinstance(line, CodeLine):
            code_lines.append(line.text.strip())
        elif isinstance(line, CodeBlockEnd):
            assert first_lineno != 0
            code_blocks.append(BashScript(first_lineno, tuple(code_lines)))
            code_lines.clear()
    if not code_blocks:
        raise NoScriptBlockFound()
    return tuple(code_blocks)


def cleanup_message(message: str) -> str:
    """Remove comments outside of code blocks."""
    lines = []
    code_line_found = False
    for line in parse_message(message):
        is_comment = line.text.startswith("#")
        if isinstance(line, CodeLine):
            if line.text.strip() and not is_comment:
                code_line_found = True
        else:
            if is_comment:
                continue
        lines.append(f"{line.text}\n")
    if not code_line_found:
        raise NoExecutableCodeFound()
    return "".join(lines)
