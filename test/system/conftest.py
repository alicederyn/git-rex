import os
import sys

import pytest

import git_rex

from .mock_editor import MockEditor


@pytest.fixture
def rex():
    def invoke_rex(*args: str):
        argv_copy = list(sys.argv)
        cwd = os.getcwd()
        try:
            sys.argv[:] = ["git-rex", *args]
            git_rex.main()
        finally:
            sys.argv[:] = argv_copy
            os.chdir(cwd)

    return invoke_rex


@pytest.fixture
def mock_editor(temp_git_repo):
    with MockEditor() as mock_editor:
        yield mock_editor
