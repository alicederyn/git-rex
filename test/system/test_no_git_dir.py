import os
from subprocess import PIPE


def test_error_message_when_no_git_dir(request, tmp_path, rex):
    os.chdir(tmp_path)
    try:
        p = rex("HEAD", stdout=PIPE, stderr=PIPE)
        stdout_bytes, stderr_bytes = p.communicate()
        assert p.returncode != 0
        stdout = stdout_bytes.decode("utf-8")
        stderr = stderr_bytes.decode("utf-8")
        assert stdout == ""
        assert (
            stderr == "fatal: not a git repository "
            "(or any of the parent directories): .git\n"
        )
    finally:
        os.chdir(request.config.invocation_dir)
