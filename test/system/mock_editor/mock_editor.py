import json
import os
import sys
from pathlib import Path
from typing import Dict

ARGV_FILE = ".git/MOCK_EDITOR_ARGV"
EXIT_CODE_FILE = ".git/MOCK_EDITOR_EXIT_CODE"
SCRIPT_DIR = Path(__file__).parent


class MockEditor:
    def __enter__(self) -> "MockEditor":
        os.mkfifo(ARGV_FILE)
        os.mkfifo(EXIT_CODE_FILE)
        self._exit_code_written = False
        return self

    def __exit__(self, type, value, traceback) -> None:
        if not self._exit_code_written:
            with open(EXIT_CODE_FILE, "w") as f:
                f.write("-1\n")

    def env(self) -> Dict[str, str]:
        return {"EDITOR": f"{sys.executable} {SCRIPT_DIR}"}

    def filename(self) -> str:
        with open(ARGV_FILE) as f:
            _, filename = json.load(f)
        assert isinstance(filename, str)
        return filename

    def exit_editor(self, return_code=0) -> None:
        with open(EXIT_CODE_FILE, "w") as f:
            f.write(f"{return_code}\n")
        self._exit_code_written = True
