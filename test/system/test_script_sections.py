"""Verify execution of multi-line code blocks."""

import os.path
from subprocess import check_call, check_output

import pytest

SINGLE_SCRIPT_COMMIT_MESSAGE = """Create foo/file.txt

```bash
mkdir foo
cd foo
echo 'New file created by rex-commit' > file.txt
```
"""


def test_section_run_as_bash_script(rex, temp_git_repo):
    check_call(["git", "commit", "--allow-empty", "-m", SINGLE_SCRIPT_COMMIT_MESSAGE])
    COMMIT = check_output(["git", "rev-parse", "HEAD"], encoding="ascii").strip()
    rex(COMMIT)

    # Verify file.txt was not created at the repository root by mistake
    assert not os.path.exists("file.txt")

    # Verify the file contains the right contents
    file_txt = open("foo/file.txt").read().splitlines()
    assert file_txt == ["New file created by rex-commit"]


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
    rex(COMMIT)

    # Verify the files contain the right contents
    file_txt = open("file.txt").read().splitlines()
    assert file_txt == ["Line appended by rex-commit"]
    subdir_file_txt = open("foo/file.txt").read().splitlines()
    assert subdir_file_txt == ["New file created by rex-commit"]


FIRST_COMMAND_FAILS_COMMIT_MESSAGE = """Fail early

```bash
false
echo 'New file created by rex-commit' > file.txt
```
"""


def test_stop_at_first_failure(rex, temp_git_repo):
    check_call(
        ["git", "commit", "--allow-empty", "-m", FIRST_COMMAND_FAILS_COMMIT_MESSAGE]
    )
    COMMIT = check_output(["git", "rev-parse", "HEAD"], encoding="ascii").strip()
    with pytest.raises(SystemExit):
        rex(COMMIT)

    # Verify second line was not run
    assert not os.path.exists("file.txt")


PIPE_FAILS_COMMIT_MESSAGE = """Pipe fails

```bash
(echo one && echo two && false) | grep t > file.txt
```
"""


def test_fail_if_any_pipe_component_fails(rex, temp_git_repo):
    check_call(["git", "commit", "--allow-empty", "-m", PIPE_FAILS_COMMIT_MESSAGE])
    COMMIT = check_output(["git", "rev-parse", "HEAD"], encoding="ascii").strip()
    with pytest.raises(SystemExit):
        rex(COMMIT)
