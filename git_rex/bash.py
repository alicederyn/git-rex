import os
from subprocess import DEVNULL, call
from typing import Tuple

TEMP_REX_SCRIPT = ".git/REX_SCRIPT"


class UserCodeError(Exception):
    def __init__(self, resultcode: int):
        self.resultcode = resultcode


def script_preamble(first_lineno: int, verbose: bool) -> str:
    preamble = [
        "set -eo pipefail",
        # Trap errors to output a failure message
        "trap '("
        # Disable set -x without outputting to stderr
        """{ STATUS=$? ; set +x ; } 2>&- ; """
        # Calculate the line number as it would have been in the original commit message
        """echo "error: $((LINENO+(%(offset)d))): """
        """'"'"'$BASH_COMMAND'"'"' returned status code $STATUS" >&2)"""
        "' ERR",
        *(["set -x"] if verbose else []),
    ]
    offset = first_lineno - len(preamble) - 1
    return "\n".join(preamble) % dict(offset=offset)


class BashScript:
    def __init__(self, first_lineno: int, script: Tuple[str, ...]):
        self.first_lineno = first_lineno
        self.script = script

    def __repr__(self):
        return (
            f"BashScript(first_lineno={self.first_lineno}, script={repr(self.script)})"
        )

    def __str__(self):
        return "\n".join(
            f"{lineno}: {line}"
            for (lineno, line) in enumerate(self.script, start=self.first_lineno)
        )

    def execute(self, *, verbose: bool = False) -> None:
        try:
            with open(TEMP_REX_SCRIPT, "w") as f:
                print(script_preamble(self.first_lineno, verbose), file=f)
                print("\n".join(self.script), file=f)
            resultcode = call(["bash", TEMP_REX_SCRIPT], stdin=DEVNULL)
            if resultcode != 0:
                raise UserCodeError(resultcode)
        finally:
            os.remove(TEMP_REX_SCRIPT)
