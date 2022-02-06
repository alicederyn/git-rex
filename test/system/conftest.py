import sys
from subprocess import Popen
from typing import Dict, Iterable, Optional

import pytest

from .mock_editor import MockEditor


class Rex:
    env: Optional[Dict[str, str]]

    def __init__(self):
        self.env = None

    def __call__(self, *args, stdout=None, stderr=None) -> Popen:
        return Popen(
            [sys.executable, "-c", "import git_rex ; git_rex.main()", *args],
            env=self.env,
            stdout=stdout,
            stderr=stderr,
        )


@pytest.fixture
def rex() -> Rex:
    return Rex()


@pytest.fixture
def mock_editor(temp_git_repo, rex: Rex) -> Iterable[MockEditor]:
    with MockEditor() as mock_editor:
        rex.env = mock_editor.env()
        yield mock_editor
