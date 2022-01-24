import re
import os
import pytest
from subprocess import check_call

from git_rex import git


@pytest.fixture
def temp_working_dir(request, tmp_path):
    os.chdir(tmp_path)
    yield
    os.chdir(request.config.invocation_dir)


def test_commit(temp_working_dir):
    check_call(["git", "init"])
    with open("file.txt", "w") as file:
        print("Test file", file=file)
    check_call(["git", "add", "file.txt"])
    check_call(["git", "config", "user.email", "unit-test-runner@example.com"])
    check_call(["git", "config", "user.name", "Unit Test Runner"])
    check_call(["git", "commit", "-m", "Added a test file"])

    c = git.Commit("HEAD")

    assert c.message == "Added a test file\n"
    assert re.match(r"^[0-9a-f]{40}$", c.hash)
