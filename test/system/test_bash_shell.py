"""Verify commands run in bash shell."""

from subprocess import check_call, check_output

COMMIT_MESSAGE = """Do something bash-specific

```bash
(diff <(grep MARK file1.txt) <(grep MARK file2.txt) || true) > file3.txt
```
"""

FILE_1_TXT = """File 1
Has some MARKED text
And an ignored line
And another ignored line
And a final MARKED line
"""


FILE_2_TXT = """File 2
Has some MARKED text
And a different ignored line
And another MARKED line
And another different ignored line
And a final MARKED line
"""


def test_commands_run_in_bash(rex, temp_git_repo):
    with open("file1.txt", "w") as f:
        print(FILE_1_TXT, file=f)
    with open("file2.txt", "w") as f:
        print(FILE_2_TXT, file=f)
    check_call(["git", "add", "-A"])
    check_call(["git", "commit", "-m", "Add file1.txt and file2.txt"])

    check_call(["git", "commit", "--allow-empty", "-m", COMMIT_MESSAGE])
    COMMIT = check_output(["git", "rev-parse", "HEAD"], encoding="ascii").strip()

    assert rex(COMMIT).wait() == 0

    file3_txt = open("file3.txt").read().splitlines()
    assert file3_txt == ["1a2", "> And another MARKED line"]
