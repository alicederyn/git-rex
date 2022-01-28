"""Verify commands receive no stdin."""

import sys
from subprocess import PIPE, Popen, check_call, check_output

import pytest

COMMIT_MESSAGE = """Try to grab input from user

```bash
cat > file.txt
```
"""


def test_no_interactive_prompts(temp_git_repo, capfd: pytest.CaptureFixture[str]):
    check_call(["git", "commit", "--allow-empty", "-m", COMMIT_MESSAGE])
    COMMIT = check_output(["git", "rev-parse", "HEAD"], encoding="ascii").strip()

    rex = Popen(
        [sys.executable, "-c", "import git_rex ; git_rex.main()", COMMIT],
        stdin=PIPE,
        encoding="utf-8",
    )
    assert rex.stdin  # Makes mypy happy
    rex.stdin.write("Some text")
    rex.stdin.close()
    assert rex.wait() == 0

    file_txt = open("file.txt").read().splitlines()
    assert file_txt == []
