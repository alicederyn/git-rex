"""Verify that rex runs scripts at the root of the repository."""

import os
from subprocess import check_call, check_output

COMMIT_MESSAGE = """An example git-rex commit

```bash
echo 'Line appended by rex-commit' >> file.txt
```
"""


def test_run_at_repository_root(rex, temp_git_repo):
    # Add and commit a simple file
    with open("file.txt", "w") as file:
        print("First line", file=file)
    check_call(["git", "add", "file.txt"])
    check_call(["git", "commit", "-m", "Initial revision of file.txt"])

    # Create a branch with a git-rex commit message
    check_call(["git", "checkout", "-b", "somebranch"])
    with open("file.txt", "w") as file:
        print("Line appended on somebranch", file=file)
    check_call(["git", "add", "file.txt"])
    check_call(["git", "commit", "--allow-empty", "-m", COMMIT_MESSAGE])

    COMMIT = check_output(["git", "rev-parse", "HEAD"], encoding="ascii").strip()

    # Switch back to main and change directory
    check_call(["git", "checkout", "main"])
    os.mkdir("subdir")
    os.chdir("subdir")

    # Run git-rex
    rex(COMMIT)

    # Verify the correct file was modified
    os.chdir("..")
    file_txt = open("file.txt").read().splitlines()
    assert file_txt == [
        "First line",
        "Line appended by rex-commit",
    ]
