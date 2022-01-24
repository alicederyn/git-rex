import re
from subprocess import check_call

from git_rex import git


def test_commit(temp_git_repo):
    with open("file.txt", "w") as file:
        print("Test file", file=file)
    check_call(["git", "add", "file.txt"])
    check_call(["git", "commit", "-m", "Added a test file"])

    c = git.Commit("HEAD")

    assert c.message == "Added a test file\n"
    assert re.match(r"^[0-9a-f]{40}$", c.hash)
