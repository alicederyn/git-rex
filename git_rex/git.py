from functools import cached_property
from pathlib import Path
from subprocess import PIPE, Popen, check_output


class GitFailure(Exception):
    def __init__(self, message: str):
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


def add_all() -> None:
    git("add", "-A")


def commit_with_meta_from(commit: "Commit") -> None:
    git("commit", "-C", commit.hash)


def top_level() -> Path:
    return Path(git("rev-parse", "--show-toplevel").decode("utf-8").removesuffix("\n"))


class Commit:
    def __init__(self, rev: str):
        self.hash = git("rev-parse", rev).decode("ascii").strip()

    @cached_property
    def message(self) -> str:
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
