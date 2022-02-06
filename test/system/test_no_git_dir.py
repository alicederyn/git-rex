import os
from subprocess import PIPE


def test_error_message_when_no_git_dir(request, tmp_path, rex):
    os.chdir(tmp_path)
    try:
        p = rex("HEAD", stdout=PIPE, stderr=PIPE, encoding="utf-8")
        stdout, stderr = p.communicate()
        assert p.returncode != 0
        assert stdout == ""
        assert (
            stderr == "fatal: not a git repository "
            "(or any of the parent directories): .git\n"
        )
    finally:
        os.chdir(request.config.invocation_dir)
