"""Git Re-EXecute

Alternative to git cherry-pick that finds and runs commands in the
commit message, instead of reapplying the diff.

Usage: git-rex COMMIT

COMMIT   Commit to reexecute
"""

import os
import re
import sys
from subprocess import DEVNULL, call

from docopt import docopt

from git_rex import git

CODE_BLOCK = re.compile(r"\s*```(\w*)\s*$")
TEMP_REX_SCRIPT = ".git/REX_SCRIPT"


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


def reexecute(commit_rev: str) -> None:
    try:
        if not git.is_clean_repo():
            print("error: cannot reexecute: You have unstaged changes.")
            print("error: Please commit or stash them.")
            sys.exit(64)
        commit = git.Commit(commit_rev)
        scripts = extract_scripts(commit.message)
        try:
            for script in scripts:
                with open(TEMP_REX_SCRIPT, "w") as f:
                    print("set -eo pipefail", file=f)
                    print("\n".join(script), file=f)
                resultcode = call(["bash", TEMP_REX_SCRIPT], stdin=DEVNULL)
                if resultcode != 0:
                    sys.exit(resultcode)
        finally:
            os.remove(TEMP_REX_SCRIPT)
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
