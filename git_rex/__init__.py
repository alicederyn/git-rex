"""Git Re-EXecute

Alternative to git cherry-pick that finds and runs commands in the
commit message, instead of reapplying the diff.

Usage: git-rex COMMIT

COMMIT   Commit to reexecute
"""

import re
import sys

from docopt import docopt
from git_rex import git


CODE_BLOCK = re.compile(r"\s*```(\w*)\s*$")


class NoCodeFound(Exception):
    pass


class ScriptError(Exception):
    def __init__(self, lineno: int, message: str):
        self.lineno = lineno
        self.message = message


def extract_script(message: str):
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
    for lineno, line in enumerate(lines):
        if not in_code_block:
            if m := CODE_BLOCK.match(line):
                if m.group(1) != "bash":
                    raise ScriptError(
                        lineno, "Code sections must be specify bash syntax"
                    )
                in_code_block = True
        else:
            if m := CODE_BLOCK.match(line):
                if m.group(1):
                    raise ScriptError(lineno, "Unexpected start of new code section")
                in_code_block = False
            elif line.strip():
                code_lines.append(line.strip())
    if not code_lines:
        raise NoCodeFound
    return tuple(code_lines)


def reexecute(commit_rev: str):
    try:
        commit = git.Commit(commit_rev)
        script = extract_script(commit.message)
        print(script)
    except NoCodeFound:
        print("fatal: No code section found in commit", file=sys.stderr)
        sys.exit(64)
    except ScriptError as e:
        print(f"fatal: {e.lineno}: {e.message}", file=sys.stderr)
        sys.exit(64)
    except git.GitFailure as e:
        print(f"fatal: {e.message}", file=sys.stderr)


def main() -> None:
    options = docopt(__doc__)
    reexecute(commit_rev=options["COMMIT"])