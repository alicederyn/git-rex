"""Verify execution of multi-line code blocks."""

from subprocess import check_call, check_output

TWO_SCRIPT_COMMIT_MESSAGE = """File manipulations

```bash
mkdir foo
cd foo
echo 'New file created by rex-commit' > file.txt
```

```bash
echo 'Line appended by rex-commit' >> file.txt
```
"""


def test_sections_run_as_separate_bash_script(rex, temp_git_repo):
    check_call(["git", "commit", "--allow-empty", "-m", TWO_SCRIPT_COMMIT_MESSAGE])
    COMMIT = check_output(["git", "rev-parse", "HEAD"], encoding="ascii").strip()
    assert rex(COMMIT).wait() == 0

    # Verify the files contain the right contents
    file_txt = open("file.txt").read().splitlines()
    assert file_txt == ["Line appended by rex-commit"]
    subdir_file_txt = open("foo/file.txt").read().splitlines()
    assert subdir_file_txt == ["New file created by rex-commit"]
