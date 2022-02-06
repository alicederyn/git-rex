"""Verify the basic invocation of rex, `git rex COMMIT`."""

from subprocess import PIPE, STDOUT, Popen, check_call, check_output

COMMIT_MESSAGE = """An example git-rex commit

Append a line of text to file.txt

```bash
echo 'Line appended by rex-commit' >> file.txt
```
"""


def test_rex_commit(rex, temp_git_repo):
    # Add and commit a simple file
    with open("file.txt", "w") as file:
        print("First line", file=file)
    check_call(["git", "add", "file.txt"])
    check_call(["git", "commit", "-m", "Initial revision of file.txt"])

    # Create a branch with a git-rex commit message
    # (Note the actual change doesn't match the message!)
    check_call(["git", "checkout", "-b", "somebranch"])
    with open("file.txt", "w") as file:
        print("Line appended on somebranch", file=file)
    check_call(["git", "add", "file.txt"])
    check_call(["git", "commit", "--allow-empty", "-m", COMMIT_MESSAGE])

    COMMIT = check_output(["git", "rev-parse", "HEAD"], encoding="ascii").strip()

    # Switch back to main and edit file.txt
    check_call(["git", "checkout", "main"])
    with open("file.txt", "a") as file:
        print("Line appended on main", file=file)
    check_call(["git", "add", "file.txt"])
    check_call(["git", "commit", "-m", "Append a line"])

    # A simple cherry-pick would fail at this point
    cherrypick = Popen(
        ["git", "cherry-pick", "-n", COMMIT],
        stdout=PIPE,
        stderr=STDOUT,
        encoding="utf-8",
    )
    stdout, _ = cherrypick.communicate()
    assert cherrypick.returncode != 0
    assert "Merge conflict in file.txt" in stdout

    check_call(["git", "reset", "--hard", "HEAD"])

    # git-rex should succeed
    assert rex(COMMIT).wait() == 0

    # Verify the file contains the right contents
    file_txt = open("file.txt").read().splitlines()
    assert file_txt == [
        "First line",
        "Line appended on main",
        "Line appended by rex-commit",
    ]

    # Verify git's history
    log = check_output(
        ["git", "log", "--format=format:%s"], encoding="ascii"
    ).splitlines()
    assert log == [
        "An example git-rex commit",
        "Append a line",
        "Initial revision of file.txt",
    ]
