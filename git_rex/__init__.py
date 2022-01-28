"""Git Re-EXecute

Alternative to git cherry-pick that finds and runs commands in the
commit message, instead of reapplying the diff.

Usage: git-rex COMMIT

COMMIT   Commit to reexecute
"""

import os
import re
import sys
from subprocess import call

from docopt import docopt

from git_rex import git

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


def extract_script(message: str) -> tuple[str, ...]:
    """Extracts code from between triple-tick blocks

    >>> commit_message = '''Sample commit
    ...
    ... This commit did some stuff
    ...
    ... ```bash
    ... run_my_code thing
    ... and_my_other thing
    ... ```
    ... '''
    >>> extract_script(commit_message)
    ('run_my_code thing', 'and_my_other thing')
    """
    in_code_block = False
    lines = message.splitlines()
    code_lines = []
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
            elif line.strip():
                code_lines.append(line.strip())
    if in_code_block:
        raise UnterminatedCodeBlock()
    if not code_lines:
        raise NoCodeFound()
    return tuple(code_lines)


def reexecute(commit_rev: str) -> None:
    try:
        if not git.is_clean_repo():
            print("error: cannot reexecute: You have unstaged changes.")
            print("error: Please commit or stash them.")
            sys.exit(64)
        commit = git.Commit(commit_rev)
        script = extract_script(commit.message)
        for line in script:
            resultcode = call(line, shell=True)
            if resultcode != 0:
                sys.exit(resultcode)
        git.add_all()
        git.commit_with_meta_from(commit)
    except NoCodeFound:
        print("fatal: No code section found in commit", file=sys.stderr)
        sys.exit(64)
    except UnsupportedCodeSyntax as e:
        print(f"fatal: {e.lineno}: Code sections must specify bash syntax")
        sys.exit(64)
    except UnexpectedCodeBlock as e:
        print(f"fatal: {e.lineno}: Unexpected start of new code section")
        sys.exit(64)
    except UnterminatedCodeBlock:
        print("fatal: Code block not terminated in commit message", file=sys.stderr)
        sys.exit(64)
    except git.GitFailure as e:
        print(f"fatal: {e.message}", file=sys.stderr)


def main() -> None:
    options = docopt(__doc__)
    os.chdir(git.top_level())
    reexecute(commit_rev=options["COMMIT"])
