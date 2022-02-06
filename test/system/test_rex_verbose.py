"""Verify the `--verbose` flag."""

from subprocess import PIPE, check_call, check_output

COMMIT_MESSAGE = """An example git-rex commit

```bash
echo 'File created by rex-commit' > file.txt
```
"""


def test_rex_commit(rex, temp_git_repo):
    check_call(["git", "commit", "--allow-empty", "-m", "Initial commit"])
    check_call(["git", "checkout", "-b", "somebranch"])
    check_call(["git", "commit", "--allow-empty", "-m", COMMIT_MESSAGE])
    COMMIT = check_output(["git", "rev-parse", "HEAD"], encoding="ascii").strip()
    check_call(["git", "checkout", "main"])

    p = rex("--verbose", COMMIT, stdout=PIPE, stderr=PIPE, encoding="utf-8")
    stdout, stderr = p.communicate()
    assert p.returncode == 0

    assert stdout == ""
    assert stderr == "+ echo 'File created by rex-commit'\n"
