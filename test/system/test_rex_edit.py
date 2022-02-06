"""Verify invoking rex with `git rex --edit`."""

from subprocess import check_output

import pytest

from .mock_editor import MockEditor

COMMIT_MESSAGE = """My commit

```bash
# This comment should be preserved
echo "Text" > file.txt
```

"""

POST_COMMIT_COMMENT = """
# This comment should be removed
"""


@pytest.mark.timeout(1)
def test_edit_flag_opens_editor(rex, mock_editor: MockEditor):
    p = rex("--edit")

    commit_file = mock_editor.filename()
    with open(commit_file) as f:
        txt = f.read()
        assert "Enter your script here" in txt

    with open(commit_file, "w") as f:
        f.write(COMMIT_MESSAGE)
        f.write(POST_COMMIT_COMMENT)

    mock_editor.exit_editor()
    assert p.wait() == 0

    # Ensure file.txt was created correctly
    with open("file.txt") as f:
        file_txt = f.read().splitlines()
    assert file_txt == ["Text"]

    # Ensure commit comments were handled correctly
    commit_message = check_output(
        ["git", "show", "-s", "--format=%B"], encoding="utf-8"
    )
    assert commit_message == COMMIT_MESSAGE
