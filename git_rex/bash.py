import os
from subprocess import DEVNULL, call
from typing import Tuple

TEMP_REX_SCRIPT = ".git/REX_SCRIPT"


class UserCodeError(Exception):
    def __init__(self, resultcode: int):
        self.resultcode = resultcode


class BashScript:
    def __init__(self, script: Tuple[str, ...]):
        self.script = script

    def __repr__(self):
        return f"BashScript({repr(self.script)})"

    def execute(self) -> None:
        try:
            with open(TEMP_REX_SCRIPT, "w") as f:
                print("set -eo pipefail", file=f)
                print("\n".join(self.script), file=f)
            resultcode = call(["bash", TEMP_REX_SCRIPT], stdin=DEVNULL)
            if resultcode != 0:
                raise UserCodeError(resultcode)
        finally:
            os.remove(TEMP_REX_SCRIPT)
