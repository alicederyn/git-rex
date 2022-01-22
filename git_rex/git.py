from subprocess import CalledProcessError, PIPE, Popen, check_output
from functools import cached_property


class GitFailure(Exception):
    def __init__(self, message):
        self.message = message


def git(*args: str) -> bytes:
    p = Popen(["git", *args], stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise GitFailure(stderr.decode("utf-8").splitlines()[0].removeprefix("fatal: "))
    return stdout


def is_clean_repo() -> bool:
    status = git("status", "--porcelain")
    return status == b""


class Commit:
    """Wrapper around Git commit commands.

    >>> c = Commit("0e507f394bd3a3a4b96fe3208d14aab469ce1ab9")
    >>> c.message
    'Initial gitignore\\n'
    """

    def __init__(self, rev: str):
        p = Popen(["git", "rev-parse", rev], stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise GitFailure(
                stderr.decode("utf-8").splitlines()[0].removeprefix("fatal: ")
            )
        self.hash = git("rev-parse", rev).decode("ascii").strip()

    @cached_property
    def message(self) -> bytes:
        return check_output(
            [
                "git",
                "show",
                "--no-patch",
                "--format=format:%B",
                "--encoding=UTF-8",
                self.hash,
            ],
            encoding="utf-8",
        )
