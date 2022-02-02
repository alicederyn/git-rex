"""Verify invoking rex with `git rex --no-commit COMMIT`."""

from subprocess import check_call, check_output

COMMIT_MESSAGE = """An example git-rex commit

Append a line of text to file.txt

```bash
echo 'File created by rex' > file.txt
```
"""


def check_output_lines(cmd):
    return check_output(cmd, encoding="ascii").splitlines()


def test_rex_commit(rex, temp_git_repo):
    # Create a commit with COMMIT_MESSAGE to reexecute
    check_call(["git", "commit", "--allow-empty", "-m", "Initial commit"])
    check_call(["git", "checkout", "-b", "somebranch"])
    check_call(["git", "commit", "--allow-empty", "-m", COMMIT_MESSAGE])
    COMMIT = check_output(["git", "rev-parse", "HEAD"], encoding="ascii").strip()
    check_call(["git", "checkout", "main"])

    # Stage a file change
    with open("file2.txt", "w") as f:
        f.write("some text")
    check_call(["git", "add", "file2.txt"])

    rex("--no-commit", COMMIT)

    # Verify the file contains the right contents
    file_txt = open("file.txt").read().splitlines()
    assert file_txt == ["File created by rex"]

    # Verify git's history
    log = check_output_lines(["git", "log", "--format=format:%s"])
    assert log == ["Initial commit"]

    # Verify the file is staged
    staged_files = check_output_lines(["git", "diff", "--name-only", "--staged"])
    unstaged_files = check_output_lines(["git", "diff", "--name-only"])
    assert set(staged_files) == {"file.txt", "file2.txt"}
    assert unstaged_files == []

    # At this point, a git commit should commit the file with the original
    # commit message
    check_call(["git", "commit", "--no-edit"])
    log = check_output_lines(["git", "log", "--format=format:%s"])
    assert log == ["An example git-rex commit", "Initial commit"]
    committed_files = check_output_lines(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]
    )
    assert set(committed_files) == {"file.txt", "file2.txt"}
