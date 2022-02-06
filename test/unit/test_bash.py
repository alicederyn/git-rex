import os
import sys
from subprocess import PIPE, Popen

import pytest

from git_rex.bash import BashScript, UserCodeError


def test_change_directory_in_script(temp_working_dir):
    script = BashScript(
        ("mkdir foo", "cd foo", "echo 'New file created by rex-commit' > file.txt")
    )
    script.execute()

    # Verify file.txt was not created at the repository root by mistake
    assert not os.path.exists("file.txt")

    # Verify the file contains the right contents
    file_txt = open("foo/file.txt").read().splitlines()
    assert file_txt == ["New file created by rex-commit"]


def test_stop_at_first_failure(temp_working_dir):
    script = BashScript(("false", "echo 'New file created by rex-commit' > file.txt"))
    with pytest.raises(UserCodeError):
        script.execute()

    # Verify second line was not run
    assert not os.path.exists("file.txt")


def test_fail_if_any_pipe_component_fails(temp_working_dir):
    script = BashScript(("(echo one && echo two && false) | grep t > file.txt",))
    with pytest.raises(UserCodeError):
        script.execute()


def test_no_interactive_prompts(temp_working_dir, capfd: pytest.CaptureFixture[str]):
    pyscript = """
        from git_rex.bash import BashScript
        script = BashScript(("cat > file.txt",))
        script.execute()
    """
    pyscript = "\n".join(line.strip() for line in pyscript.strip().splitlines())
    py = Popen([sys.executable, "-c", pyscript], stdin=PIPE, encoding="utf-8")
    assert py.stdin  # Makes mypy happy
    py.stdin.write("Some text")
    py.stdin.close()
    assert py.wait() == 0

    file_txt = open("file.txt").read().splitlines()
    assert file_txt == []
