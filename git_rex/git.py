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
        try:
            raise GitFailure(
                stderr.decode("utf-8").splitlines()[0].removeprefix("fatal: ")
            )
        except IndexError:
            raise GitFailure("") from None
    return stdout


def is_clean_repo() -> bool:
    status = git("status", "--porcelain")
    return status == b""


def no_unstaged_changes() -> bool:
    status = git("status", "--porcelain")
    return any(line[1] != " " for line in status.splitlines())


def add_all() -> None:
    git("add", "-A")


def core_editor() -> str:
    p = Popen(["git", "config", "core.editor"], stdout=PIPE)
    stdout, _ = p.communicate()
    return stdout.decode("ascii").strip()


def store_commit_message(commit_message: str) -> None:
    with open(".git/MERGE_MSG", "w") as f:
        f.write(commit_message)


def commit(commit_message: str) -> None:
    git("commit", "-m", commit_message)


def commit_with_meta_from(commit: "Commit") -> None:
    git("commit", "-C", commit.hash)


def top_level() -> Path:
    return Path(git("rev-parse", "--show-toplevel").decode("utf-8").removesuffix("\n"))


class Commit:
    def __init__(self, rev: str):
        self._rev = rev

    @cached_property
    def hash(self) -> str:
        return git("rev-parse", self._rev).decode("ascii").strip()

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
