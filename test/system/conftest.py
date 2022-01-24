import sys

import pytest

import git_rex


@pytest.fixture
def rex():
    def invoke_rex(*args: str):
        argv_copy = list(sys.argv)
        try:
            sys.argv[:] = ["git-rex", *args]
            git_rex.main()
        finally:
            sys.argv[:] = argv_copy

    return invoke_rex
